from . import (
    PPD_PRODUCT, PPD_MANUFACTURER, PPD_MODEL, 
    PPD_SHORT_NICKNAME, PPD_NICKNAME, PPD_1284_DEVICE_ID
)

# 导入翻译模块 - Import translation module
try:
    from .translations import t
except ImportError:
    def t(key, **kwargs):
        return key


class PPD(object):
    def text(self):
        raise NotImplementedError()


class BasicPostscriptPPD(PPD):
    product = PPD_PRODUCT
    manufacturer = PPD_MANUFACTURER
    model = PPD_MODEL

    def text(self):
        template = '''*PPD-Adobe: "4.3"

*{ppd_file_header}
*%% and is almost certainly missing lots of features

*%%     ___________
*%%    |           |
*%%    | PPD File. |
*%%    |           |
*%%  (============(@|
*%%  |            | |
*%%  | [        ] | |
*%%  |____________|/
*%%

*%% About this PPD file
*LanguageLevel: "3"
*LanguageEncoding: ISOLatin1
*LanguageVersion: English
*PCFileName: "{ppdfilename}"
*PSVersion: "(3010.000) 3"
*PSVersion: "(3010.000) 550"
*PSVersion: "(3010.000) 1000"

*{ppd_printer_name}
*Product: "{product}"
*Manufacturer:  "{manufacturer}"
*ModelName: "{model}"

*{ppd_windows_id_info}
*ShortNickName: "{short_nickname}"
*NickName: "{nickname}"
*1284DeviceID: "{device_id}"
*cupsVersion: 2.3

*{ppd_color_support}
*ColorDevice: True
*DefaultColorSpace: CMYK
*Throughput: "1"
*Password: "0"
*cupsManualCopies: False
*cupsModelNumber: 2

*{ppd_windows_color_matching}
*ColorModel: *ColorModel CMYK/CMYK Color
*DefaultColorModel: CMYK
*cupsColorOrder: 0
*cupsColorSpace: 0
*cupsColorProfile: ""

*{ppd_extended_windows_support}
*cupsFilter2: "application/vnd.cups-postscript 0 -"
*cupsFilter2: "application/pdf 100 -"
*cupsFilter2: "image/jpeg 100 -"
*cupsFilter2: "image/png 100 -"
*cupsFilter2: "image/tiff 100 -"
*cupsFilter2: "image/gif 100 -"
*cupsFilter2: "image/bmp 100 -"

*{ppd_windows_photo_viewer}
*APPrinterMimeTypes: "image/jpeg,image/png,image/tiff,image/bmp,image/gif,application/pdf"
*APSupportsMimeTypes: "image/jpeg,image/png,image/tiff,image/bmp,image/gif,application/pdf"

*{ppd_windows_photo_print_key}
*cupsPrintQuality: 6
*cupsCompression: 1
*cupsEvenDuplex: False
*cupsBorderless: True
*cupsPhotoOptimized: True

*{ppd_supported_paper_sizes}
*DefaultPaperSize: A4
*PaperDimension A4/A4: "595.28 841.89"
*PaperDimension A3/A3: "841.89 1190.55"
*PaperDimension Letter/Letter: "612.00 792.00"
*PaperDimension Legal/Legal: "612.00 1008.00"
*PaperDimension Executive/Executive: "522.00 756.00"
*PaperDimension Photo4x6/4x6in: "288.00 432.00"
*PaperDimension Photo5x7/5x7in: "360.00 504.00"
*PaperDimension Photo8x10/8x10in: "576.00 720.00"
*PaperDimension Photo10x15/10x15cm: "283.46 425.19"
*PaperDimension Photo13x18/13x18cm: "368.50 510.24"
*PaperDimension Photo15x20/15x20cm: "425.19 566.93"

*{ppd_imageable_areas}
*ImageableArea A4/A4: "14.17 14.17 581.10 827.72"
*ImageableArea A3/A3: "14.17 14.17 827.72 1176.38"
*ImageableArea Letter/Letter: "14.17 14.17 597.83 777.83"
*ImageableArea Legal/Legal: "14.17 14.17 597.83 993.83"
*ImageableArea Executive/Executive: "14.17 14.17 507.83 741.83"
*ImageableArea Photo4x6/4x6in: "0 0 288.00 432.00"  # 无边框照片
*ImageableArea Photo5x7/5x7in: "0 0 360.00 504.00"
*ImageableArea Photo8x10/8x10in: "0 0 576.00 720.00"
*ImageableArea Photo10x15/10x15cm: "0 0 283.46 425.19"
*ImageableArea Photo13x18/13x18cm: "0 0 368.50 510.24"
*ImageableArea Photo15x20/15x20cm: "0 0 411.02 552.76"

*{ppd_page_size_selection}
*OpenUI *PageSize/Page Size: PickOne
*OrderDependency: 10 AnySetup *PageSize
*DefaultPageSize: A4
*PageSize A4/A4: "<</PageSize[595.28 841.89]/ImagingBBox null>>setpagedevice"
*PageSize A3/A3: "<</PageSize[841.89 1190.55]/ImagingBBox null>>setpagedevice"
*PageSize Letter/Letter: "<</PageSize[612.00 792.00]/ImagingBBox null>>setpagedevice"
*PageSize Legal/Legal: "<</PageSize[612.00 1008.00]/ImagingBBox null>>setpagedevice"
*PageSize Executive/Executive: "<</PageSize[522.00 756.00]/ImagingBBox null>>setpagedevice"
*PageSize Photo4x6/4x6in: "<</PageSize[288.00 432.00]/ImagingBBox[0 0 288.00 432.00]>>setpagedevice"
*PageSize Photo5x7/5x7in: "<</PageSize[360.00 504.00]/ImagingBBox[0 0 360.00 504.00]>>setpagedevice"
*PageSize Photo8x10/8x10in: "<</PageSize[576.00 720.00]/ImagingBBox[0 0 576.00 720.00]>>setpagedevice"
*PageSize Photo10x15/10x15cm: "<</PageSize[283.46 425.19]/ImagingBBox[0 0 283.46 425.19]>>setpagedevice"
*PageSize Photo13x18/13x18cm: "<</PageSize[368.50 510.24]/ImagingBBox[0 0 368.50 510.24]>>setpagedevice"
*PageSize Photo15x20/15x20cm: "<</PageSize[425.19 566.93]/ImagingBBox[0 0 425.19 566.93]>>setpagedevice"
*CloseUI: *PageSize

*{ppd_page_region}
*OpenUI *PageRegion/Page Region: PickOne
*OrderDependency: 10 AnySetup *PageRegion
*DefaultPageRegion: A4
*PageRegion A4/A4: "<</PageRegion[595.28 841.89]/ImagingBBox null>>setpagedevice"
*PageRegion A3/A3: "<</PageRegion[841.89 1190.55]/ImagingBBox null>>setpagedevice"
*PageRegion Letter/Letter: "<</PageRegion[612.00 792.00]/ImagingBBox null>>setpagedevice"
*PageRegion Legal/Legal: "<</PageRegion[612.00 1008.00]/ImagingBBox null>>setpagedevice"
*PageRegion Executive/Executive: "<</PageRegion[522.00 756.00]/ImagingBBox null>>setpagedevice"
*PageRegion Photo4x6/4x6in: "<</PageRegion[288.00 432.00]/ImagingBBox[0 0 288.00 432.00]>>setpagedevice"
*PageRegion Photo5x7/5x7in: "<</PageRegion[360.00 504.00]/ImagingBBox[0 0 360.00 504.00]>>setpagedevice"
*PageRegion Photo8x10/8x10in: "<</PageRegion[576.00 720.00]/ImagingBBox[0 0 576.00 720.00]>>setpagedevice"
*PageRegion Photo10x15/10x15cm: "<</PageRegion[283.46 425.19]/ImagingBBox[0 0 283.46 425.19]>>setpagedevice"
*PageRegion Photo13x18/13x18cm: "<</PageRegion[368.50 510.24]/ImagingBBox[0 0 368.50 510.24]>>setpagedevice"
*PageRegion Photo15x20/15x20cm: "<</PageRegion[425.19 566.93]/ImagingBBox[0 0 425.19 566.93]>>setpagedevice"
*CloseUI: *PageRegion

*{ppd_input_slots}
*OpenUI *InputSlot/Media Source: PickOne
*OrderDependency: 10 AnySetup *InputSlot
*DefaultInputSlot: Tray1
*InputSlot Auto/Auto: "<</ManualFeed false>>setpagedevice"
*InputSlot Tray1/Tray 1: "<</MediaPosition 1>>setpagedevice"
*InputSlot Tray2/Tray 2: "<</MediaPosition 2>>setpagedevice"
*InputSlot Manual/Manual Feed: "<</ManualFeed true>>setpagedevice"
*InputSlot PhotoTray/Photo Tray: "<</MediaPosition 3>>setpagedevice"
*CloseUI: *InputSlot

*{ppd_resolution_settings}
*OpenUI *Resolution/Resolution: PickOne
*OrderDependency: 10 AnySetup *Resolution
*DefaultResolution: 600dpi
*Resolution 300dpi/300 DPI: "<</HWResolution[300 300]>>setpagedevice"
*Resolution 600dpi/600 DPI: "<</HWResolution[600 600]>>setpagedevice"
*Resolution 1200dpi/1200 DPI: "<</HWResolution[1200 1200]>>setpagedevice"
*Resolution 2400dpi/2400 DPI: "<</HWResolution[2400 2400]>>setpagedevice"
*Resolution 4800dpi/4800 DPI: "<</HWResolution[4800 4800]>>setpagedevice"
*CloseUI: *Resolution

*{ppd_color_model}
*OpenUI *ColorModel/Color Model: PickOne
*OrderDependency: 100 AnySetup *ColorModel
*DefaultColorModel: CMYK
*ColorModel CMYK/CMYK Color: 
    "<</ProcessColorModel /DeviceCMYK /HWColorSettings [0 0 0 0]>>setpagedevice"
*ColorModel RGB/RGB Color: 
    "<</ProcessColorModel /DeviceRGB /HWColorSettings [1 1 1]>>setpagedevice"
*ColorModel Gray/Grayscale: 
    "<</ProcessColorModel /DeviceGray /HWColorSettings [2 2 2]>>setpagedevice"
*ColorModel PhotoCMYK/Photo CMYK: 
    "<</ProcessColorModel /DeviceCMYK /HWColorSettings [3 3 3]>>setpagedevice"
*ColorModel PhotoRGB/Photo RGB: 
    "<</ProcessColorModel /DeviceRGB /HWColorSettings [4 4 4]>>setpagedevice"
*CloseUI: *ColorModel

*{ppd_print_quality}
*OpenUI *PrintQuality/Print Quality: PickOne
*OrderDependency: 10 AnySetup *PrintQuality
*DefaultPrintQuality: Normal
*PrintQuality Draft/Draft: "<</cupsPrintQuality 3>>setpagedevice"
*PrintQuality Normal/Normal: "<</cupsPrintQuality 4>>setpagedevice"
*PrintQuality High/High: "<</cupsPrintQuality 5>>setpagedevice"
*PrintQuality Photo/Photo Quality: "<</cupsPrintQuality 6>>setpagedevice"
*CloseUI: *PrintQuality

*{ppd_copies_settings}
*DefaultCopies: 1
*MaxCopies: 99
*Copies 1/1: "1"
*Copies 2/2: "2"
*Copies 5/5: "5"
*Copies 10/10: "10"

*{ppd_media_types}
*OpenUI *MediaType/Media Type: PickOne
*OrderDependency: 10 AnySetup *MediaType
*DefaultMediaType: Plain
*MediaType Plain/Plain Paper: "<</MediaType (Plain)>>setpagedevice"
*MediaType Photo/Photo Paper: "<</MediaType (Photo)>>setpagedevice"
*MediaType Glossy/Glossy Paper: "<</MediaType (Glossy)>>setpagedevice"
*MediaType Matte/Matte Paper: "<</MediaType (Matte)>>setpagedevice"
*MediaType Transparency/Transparency Film: "<</MediaType (Transparency)>>setpagedevice"
*CloseUI: *MediaType

*{ppd_windows_photo_filters}
*cupsFilter2: "image/jpeg application/vnd.cups-pdf 100 pdftopdf"
*cupsFilter2: "image/png application/vnd.cups-pdf 100 pdftopdf"
*cupsFilter2: "image/tiff application/vnd.cups-pdf 100 pdftopdf"
*cupsFilter2: "image/bmp application/vnd.cups-pdf 100 pdftopdf"
*cupsFilter2: "image/gif application/vnd.cups-pdf 100 pdftopdf"

*{ppd_generic_pdf_filters}
*cupsFilter2: "application/pdf application/vnd.cups-pdf 0 pdftopdf"
*cupsFilter2: "application/postscript application/vnd.cups-pdf 50 pstopdf"
*cupsFilter2: "text/plain application/vnd.cups-pdf 90 texttopdf"

*{ppd_windows_gdi_printing}
*cupsGDIBackingStore: True
*cupsGDIAlwaysRGB: True
*cupsGDIColorFormat: 0
*cupsGDIDitherAlg: 0
*cupsGDIDitherType: 0
*cupsGDIHalftone: 0
*cupsGDIInversion: 0
*cupsGDILogicOperation: 0
*cupsGDINegative: False
*cupsGDIOptimize: True
*cupsGDIPalette: 0
*cupsGDIRaster: 0
*cupsGDIUCR: 0

*{ppd_duplex_support}
*OpenUI *Duplex/Double-Sided Printing: PickOne
*OrderDependency: 10 AnySetup *Duplex
*DefaultDuplex: None
*Duplex None/Off: "<</Duplex false>>setpagedevice"
*Duplex DuplexNoTumble/Long Edge: "<</Duplex true/Tumble false>>setpagedevice"
*Duplex DuplexTumble/Short Edge: "<</Duplex true/Tumble true>>setpagedevice"
*CloseUI: *Duplex

*{ppd_windows_photo_specific}
*cupsBorderlessScalingFactor: 100
*cupsBorderless: True
*cupsPhotoOptimized: True
*cupsPhotoRenderingIntent: 0
*cupsPhotoBW: False  # 关键：强制禁用黑白照片模式

*{ppd_finishing_options}
*OpenUI *cupsFinishing/Finishing: PickOne
*OrderDependency: 100 AnySetup *cupsFinishing
*DefaultcupsFinishing: None
*cupsFinishing None/None: ""
*cupsFinishing Staple/Staple: "<</Staple 1>>"
*cupsFinishing Punch/Punch: "<</Punch 1>>"
*CloseUI: *cupsFinishing

*{ppd_job_template_support}
*APJobSetup: True
*APPrinterMimeTypes: "image/jpeg,image/png,image/tiff,image/bmp,image/gif,application/pdf"
*APSupportsMimeTypes: "image/jpeg,image/png,image/tiff,image/bmp,image/gif,application/pdf"

*{ppd_windows_registry_compatibility}
*RegistryDword "Printer Driver Data" "ColorMatrix": 1
*RegistryDword "Printer Driver Data" "ColorSupport": 3
*RegistryDword "Printer Driver Data" "PhotoColorMode": 1
*RegistryDword "Printer Driver Data" "PhotoOptimized": 1
*RegistryDword "Printer Driver Data" "PhotoPaperSize": 1
*RegistryDword "Printer Driver Data" "PhotoQuality": 6

*{ppd_output_order}
*OutputOrder: Normal

*{ppd_paper_handling}
*OpenUI *cupsMediaPosition/Media Position: PickOne
*OrderDependency: 10 AnySetup *cupsMediaPosition
*DefaultcupsMediaPosition: 0
*cupsMediaPosition 0/Top Output Bin: ""
*cupsMediaPosition 1/Bottom Output Bin: ""
*cupsMediaPosition 2/Envelope Feeder: ""
*cupsMediaPosition 3/Photo Tray: ""
*CloseUI: *cupsMediaPosition

*{ppd_stapling_offset}
*StapleLocation: SinglePortrait

*{ppd_installable_options}
*CloseGroup: General

*{ppd_end_marker}
*%%End
'''
        
        return template.format(
            product=self.product,
            manufacturer=self.manufacturer,
            model=self.model,
            ppdfilename=f"{self.model}.ppd",
            short_nickname=PPD_SHORT_NICKNAME,
            nickname=PPD_NICKNAME,
            device_id=PPD_1284_DEVICE_ID.format(
                manufacturer=self.manufacturer,
                model=self.model
            ),
            ppd_file_header=t('ppd_file_header'),
        ).encode('utf-8')


class BasicPdfPPD(BasicPostscriptPPD):
    model = PPD_MODEL

    def text(self):
        # 使用父类的text方法，已经包含PDF过滤器和扩展功能 - Use parent class text method, already includes PDF filters and extended functionality
        return super().text()