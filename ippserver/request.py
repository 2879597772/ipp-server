from io import BytesIO
import operator
import itertools

from .parsers import read_struct, write_struct
from .constants import SectionEnum, TagEnum, IppVersionEnum

# 导入翻译模块 - Import translation module
try:
    from .translations import t
except ImportError:
    def t(key, **kwargs):
        return key


class IppRequest(object):
    def __init__(self, version, opid_or_status, request_id, attributes):
        self.version = version  # (major, minor)
        self.opid_or_status = opid_or_status
        self.request_id = request_id
        self._attributes = attributes

    def __eq__(self, other):
        if not isinstance(other, IppRequest):
            return False
        return (self.version == other.version and
                self.opid_or_status == other.opid_or_status and
                self.request_id == other.request_id and
                self._attributes == other._attributes)

    def __repr__(self):
        return 'IppRequest(%r, 0x%04x, 0x%02x, %r)' % (
            self.version,
            self.opid_or_status,
            self.request_id,
            self._attributes,)

    @classmethod
    def from_string(cls, string):
        return cls.from_file(BytesIO(string))

    @classmethod
    def from_file(cls, f):
        version_major, version_minor = read_struct(f, b'>bb')
        version = (version_major, version_minor)
        
        # Check if version is supported - 检查版本是否支持
        version_code = (version_major << 8) | version_minor
        if version_code not in [v.value for v in IppVersionEnum]:
            # RFC 8011: If version is not supported, respond with server-error-version-not-supported
            # RFC 8011：如果版本不支持，使用server-error-version-not-supported响应
            # But we still parse the request to get the request_id - 但我们仍然解析请求以获取request_id
            pass
        
        operation_id_or_status_code, request_id = read_struct(f, b'>hi')

        attributes = {}
        current_section = None
        current_name = None
        while True:
            tag, = read_struct(f, b'>B')

            if tag == SectionEnum.END:
                break
            elif SectionEnum.is_section_tag(tag):
                current_section = tag
                current_name = None
            else:
                if current_section is None:
                    raise Exception(t('request_no_section_delimiter'))

                name_len, = read_struct(f, b'>h')
                if name_len == 0:
                    if current_name is None:
                        raise Exception(t('request_additional_attribute_needs_name'))
                    else:
                        # additional attribute, under the same name - 附加属性，使用相同的名称
                        pass
                else:
                    current_name = f.read(name_len)

                value_len, = read_struct(f, b'>h')
                value_str = f.read(value_len)
                attributes.setdefault((current_section, current_name, tag), []).append(value_str)

        return cls(version, operation_id_or_status_code, request_id, attributes)

    def to_string(self):
        sio = BytesIO()
        self.to_file(sio)
        return sio.getvalue()

    def to_file(self, f):
        version_major, version_minor = self.version
        write_struct(f, b'>bb', version_major, version_minor)
        write_struct(f, b'>hi', self.opid_or_status, self.request_id)

        for section, attrs_in_section in itertools.groupby(
            sorted(self._attributes.keys()), operator.itemgetter(0)
        ):
            write_struct(f, b'>B', section)
            for key in attrs_in_section:
                _section, name, tag = key
                for i, value in enumerate(self._attributes[key]):
                    write_struct(f, b'>B', tag)
                    if i == 0:
                        write_struct(f, b'>h', len(name))
                        f.write(name)
                    else:
                        write_struct(f, b'>h', 0)
                    # Integer must be 4 bytes - 整数必须为4字节
                    if tag == TagEnum.integer and len(value) != 4:
                        raise ValueError(t('parser_integer_value_error', length=len(value)))
                    write_struct(f, b'>h', len(value))
                    f.write(value)
        write_struct(f, b'>B', SectionEnum.END)

    def attributes_to_multilevel(self, section=None):
        ret = {}
        for key in self._attributes.keys():
            if section and section != key[0]:
                continue
            ret.setdefault(key[0], {})
            ret[key[0]].setdefault(key[1], {})
            ret[key[0]][key[1]][key[2]] = self._attributes[key]
        return ret

    def lookup(self, section, name, tag):
        return self._attributes.get((section, name, tag), [])

    def only(self, section, name, tag):
        items = self.lookup(section, name, tag)
        if len(items) == 1:
            return items[0]
        elif len(items) == 0:
            raise RuntimeError(t('request_attributes_key_error', 
                               section=repr(section), name=repr(name), tag=repr(tag)))
        else:
            raise ValueError(t('request_attributes_multiple_values',
                             section=repr(section), name=repr(name), tag=repr(tag)))
    
    def get_version_code(self):
        """Get IPP version as integer code - 获取IPP版本作为整数代码"""
        return (self.version[0] << 8) | self.version[1]