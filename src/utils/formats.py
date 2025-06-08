def float_array_input_validate(input):        
    try:
        for s in input.split(","):
            str2flt(s.strip())
        return True
    except ValueError:
        return False        

def int_array_input_validate(input):        
    try:
        for s in input.split(","):
            str2int(s.strip())
        return True
    except ValueError:
        return False
            
def positive_float_input_validate(input):        
    try:
        val = str2flt(input.strip())
        if val <= 0:
            return False                
        return True
    except ValueError:
        return False
    
def nonneg_float_input_validate(input):        
    try:
        val = str2flt(input.strip())
        if val < 0:
            return False                
        return True
    except ValueError:
        return False
    
def float_input_validate(input):        
    try:
        str2flt(input.strip())         
        return True
    except ValueError:
        return False
        
def positive_int_input_validate(input):        
    try:
        val = str2flt(input.strip())
        if val <= 0:
            return False                
        return True
    except ValueError:
        return False
    
def nonzero_float_input_validate(input):        
    try:
        val = str2flt(input.strip())
        if val == 0:
            return False                
        return True
    except ValueError:
        return False
    
def str2flt(s):
    try:
        if ( s.strip()!="" and s.strip()!="." and s.strip()!="-" and s.strip()!="+"):
            return float(s)
        else:
            return 0.0
    except ValueError:
        raise

def str2int(s):
    try:
        if ( s.strip()!="" and s.strip()!="+"):
            return int(s)
        else:
            return 0
    except ValueError:
        raise
    
def int_arr_to_str(input):
    return ', '.join( ( "%6d" % x ) for x in input)

def flt_arr_to_str(input, factor = 1.0):
    return ', '.join( ( "%6.2f" % (x*factor) ) for x in input )

def str_to_int_arr(input):
    return [ str2int(s.strip()) for s in input.split(",")  ] 

def str_to_flt_arr(input, factor = 1.0):
    return [ str2flt(s.strip())*factor for s in input.split(",")  ] 