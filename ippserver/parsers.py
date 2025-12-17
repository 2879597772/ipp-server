import struct
import datetime
import time

# 导入翻译模块 - Import translation module
try:
    from .translations import t
except ImportError:
    def t(key, **kwargs):
        return key


def read_struct(f, fmt):
    """读取结构数据 - Read structured data"""
    sz = struct.calcsize(fmt)
    string = f.read(sz)
    return struct.unpack(fmt, string)


def write_struct(f, fmt, *args):
    """写入结构数据 - Write structured data"""
    data = struct.pack(fmt, *args)
    f.write(data)


class Value(object):
    @classmethod
    def from_bytes(cls, _data):
        raise NotImplementedError()

    def bytes(self):
        raise NotImplementedError()

    def __bytes__(self):
        return self.bytes()


class Boolean(Value):
    def __init__(self, value):
        assert isinstance(value, bool)
        self.boolean = value
        Value.__init__(self)

    @classmethod
    def from_bytes(cls, data):
        val, = struct.unpack(b'>b', data)
        return cls(bool(val))

    def bytes(self):
        return struct.pack(b'>b', 1 if self.boolean else 0)


class Integer(Value):
    def __init__(self, value):
        assert isinstance(value, int)
        self.integer = value
        Value.__init__(self)

    @classmethod
    def from_bytes(cls, data):
        val, = struct.unpack(b'>i', data)
        return cls(val)

    def bytes(self):
        return struct.pack(b'>i', self.integer)


class Enum(Integer):
    pass


class DateTime(Value):
    """IPP DateTime type - RFC 2579 - IPP DateTime类型 - RFC 2579"""
    
    def __init__(self, value=None):
        if value is None:
            value = datetime.datetime.now()
        elif isinstance(value, (int, float)):
            value = datetime.datetime.fromtimestamp(value)
        
        assert isinstance(value, datetime.datetime)
        self.datetime = value
        Value.__init__(self)
    
    @classmethod
    def from_bytes(cls, data):
        if len(data) != 11:
            raise ValueError(t('parser_datetime_value_error', length=len(data)))
        
        year, month, day, hour, minute, second, deci_second, direction, tz_hour, tz_minute = \
            struct.unpack(b'>hBBBBBBcBB', data)
        
        # Convert from UTC to datetime - 从UTC转换为datetime
        # Note: IPP DateTime uses local time with timezone offset - 注意：IPP DateTime使用带时区偏移的本地时间
        dt = datetime.datetime(year, month, day, hour, minute, second, deci_second * 10000)
        
        # Apply timezone offset (simplified handling) - 应用时区偏移（简化处理）
        # In production, should properly handle timezone conversion - 在生产环境中，应正确处理时区转换
        return cls(dt)
    
    def bytes(self):
        dt = self.datetime
        year = dt.year
        month = dt.month
        day = dt.day
        hour = dt.hour
        minute = dt.minute
        second = dt.second
        deci_second = dt.microsecond // 10000
        
        # For simplicity, assume UTC (+00:00) - 为简化，假设为UTC (+00:00)
        direction = b'+'
        tz_hour = 0
        tz_minute = 0
        
        return struct.pack(b'>hBBBBBBcBB', year, month, day, hour, minute, 
                          second, deci_second, direction, tz_hour, tz_minute)
    
    @classmethod
    def now(cls):
        return cls(datetime.datetime.now())


class Resolution(Value):
    """IPP Resolution type - IPP Resolution类型"""
    
    def __init__(self, cross_feed_resolution, feed_resolution, units):
        """
        units: 3 = dots per inch, 4 = dots per centimeter - 单位：3 = 每英寸点数，4 = 每厘米点数
        """
        self.cross_feed_resolution = cross_feed_resolution
        self.feed_resolution = feed_resolution
        self.units = units
        Value.__init__(self)
    
    @classmethod
    def from_bytes(cls, data):
        if len(data) != 9:
            raise ValueError(t('parser_resolution_value_error', length=len(data)))
        
        cross_feed, feed_resolution, units = struct.unpack(b'>iiB', data)
        return cls(cross_feed, feed_resolution, units)
    
    def bytes(self):
        return struct.pack(b'>iiB', self.cross_feed_resolution, 
                          self.feed_resolution, self.units)


class RangeOfInteger(Value):
    """IPP RangeOfInteger type - IPP RangeOfInteger类型"""
    
    def __init__(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        Value.__init__(self)
    
    @classmethod
    def from_bytes(cls, data):
        if len(data) != 8:
            raise ValueError(t('parser_range_of_integer_error', length=len(data)))
        
        lower_bound, upper_bound = struct.unpack(b'>ii', data)
        return cls(lower_bound, upper_bound)
    
    def bytes(self):
        return struct.pack(b'>ii', self.lower_bound, self.upper_bound)