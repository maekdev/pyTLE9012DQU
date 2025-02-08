# tle9012dqu_reg.py
#
# 240104
# markus ekler
#
# register description in human readable format
# can be used to implement low-level functions
#

REG = {
	"PART_CONFIG"		: 0x01,
	"OL_OV_THR"			: 0x02,
	"OL_UV_THR"			: 0x03,
	"TEMP_CONF"			: 0x04,
	"INT_OT_WARN_CONF"	: 0x05,
	"RR_ERR_CNT"		: 0x08,
	"RR_CONFIG"			: 0x09,
	"FAULT_MASK"		: 0x0a,
	"GEN_DIAG"			: 0x0b,
	"CELL_UV"			: 0x0c,
	"CELL_OV"			: 0x0d,
	"EXT_TEMP_DIAG"		: 0x0e,
	"DIAG_OL"			: 0x10,
	"REG_CRC_ERR"		: 0x11,
	"CELL_UV_DAC_COMP"	: 0x12,
	"CELL_OV_DAC_COMP"	: 0x13,
	"OP_MODE"			: 0x14,
	"BAL_CURR_THR"		: 0x15,
	"BAL_SETTINGS"		: 0x16,
	"AVM_CONFIG"		: 0x17,
	"MEAS_CTRL"			: 0x18,
	"PCVM_0"			: 0x19,
	"PCVM_1"			: 0x1a,
	"PCVM_2"			: 0x1b,
	"PCVM_3"			: 0x1c,
	"PCVM_4"			: 0x1d,
	"PCVM_5"			: 0x1e,
	"PCVM_6"			: 0x1f,
	"PCVM_7"			: 0x20,
	"PCVM_8"			: 0x21,
	"PCVM_9"			: 0x22,
	"PCVM_10"			: 0x23,
	"PCVM_11"			: 0x24,
	"SCVM_HIGH"			: 0x25,
	"SCVM_LOW"			: 0x26,
	"STRESS_PCVM"		: 0x27,
	"BVM"				: 0x28,
	"EXT_TEMP_0"		: 0x29,
	"EXT_TEMP_1"		: 0x2a,
	"EXT_TEMP_2"		: 0x2b,
	"EXT_TEMP_3"		: 0x2c,
	"EXT_TEMP_4"		: 0x2d,
	"EXT_TEMP_R_DIAG"	: 0x2f,
	"INT_TEMP"			: 0x30,
	"MULTI_READ"		: 0x31,
	"MULTI_READ_CFG"	: 0x32,
	"BAL_DIAG_OC"		: 0x33,
	"BAL_DIAG_UC"		: 0x34,
	"INT_TEMP_2"		: 0x35,
	"CONFIG"			: 0x36,
	"GPIO"				: 0x37,
	"GPIO_PWM"			: 0x38,
	"ICVID"				: 0x39,
	"MAILBOX"			: 0x3a,
	"CUST_ID_0"			: 0x3b,
	"CUST_ID_1"			: 0x3c,
	"WDOG_CNT"			: 0x3d,
	"SCVM_CONFIG"		: 0x3e,
	"STRESS_AUX"		: 0x3f,
	"BAL_PWM"			: 0x5b,
	"BAL_CNT_0"			: 0x5c,
	"BAL_CNT_1"			: 0x5d,
	"BAL_CNT_2"			: 0x5e,
	"BAL_CNT_3"			: 0x5f
}

def ADDR2REGNAME(addr):
	for k1 in REG.keys():
		if REG[k1] == addr: return k1
	return None
