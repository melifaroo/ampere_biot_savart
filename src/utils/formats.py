def float_array_input_validate(str):        
    try:
        if not str.strip() == "":
            for s in str.split(","):
                str_to_flt(s.strip())
        return True
    except ValueError:
        return False        

def int_array_input_validate(str):        
    try:
        if not str.strip() == "":
            for s in str.split(","):
                str_to_int(s.strip())
        return True
    except ValueError:
        return False
            
def positive_float_input_validate(str):        
    try:
        val = str_to_flt(str.strip())
        if val <= 0:
            return False                
        return True
    except ValueError:
        return False
    
def nonneg_float_input_validate(str):        
    try:
        val = str_to_flt(str.strip())
        if val < 0:
            return False                
        return True
    except ValueError:
        return False
    
def float_input_validate(str):        
    try:
        str_to_flt(str.strip())         
        return True
    except ValueError:
        return False
        
def positive_int_input_validate(str):        
    try:
        val = str_to_flt(str.strip())
        if val <= 0:
            return False                
        return True
    except ValueError:
        return False
    
def nonzero_float_input_validate(str):        
    try:
        val = str_to_flt(str.strip())
        if val == 0:
            return False                
        return True
    except ValueError:
        return False
    
def str_to_flt(s):
    try:
        if ( s.strip()!="" and s.strip()!="." and s.strip()!="-" and s.strip()!="+"):
            return float(s)
        else:
            return 0.0
    except ValueError:
        raise

def str_to_int(s):
    try:
        if ( s.strip()!="" and s.strip()!="+"):
            return int(s)
        else:
            return 0
    except ValueError:
        raise
    
def flt_to_str(x):
    return "%6.2f" % x 
        
def int_arr_to_str(arr):
    return ', '.join( ( "%6d" % x ) for x in arr)

def flt_arr_to_str(arr, factor = 1.0):
    return ', '.join( ( "%6.2f" % (x*factor) ) for x in arr )

def str_to_int_arr(str):
    return [ str_to_int(s.strip()) for s in str.split(",") ] if not str.strip()=="" else []

def str_to_flt_arr(str, factor = 1.0):
    return [ str_to_flt(s.strip())*factor for s in str.split(",") ] if not str.strip()=="" else []

def length_str_arr(str):
    return len(str.split(",")) if not str.strip()=="" else 0