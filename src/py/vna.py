import numpy as np
import os
from io import BytesIO


def impedance2gamma(Z, Z0):
  """
  Name: vna.impedance2gamma()

  Args: Z   - impedance
        Z0  - reference impedance (usually 50 Ohms)
  """
  return (Z-Z0)/(Z+Z0)


def gamma2impedance(r, Z0):
  """
  Name: vna.gamma2impedence()

  Args: r   - Gamma
        Z0  - reference impedance (usually 50 Ohms)
  """
  return Z0*(1+r)/(1-r)


def gamma_de_embed(s11, s12s21, s22, rp):
  """
  Name: vna.gamma_de_embed()

  Args: s11
        s12s21
        s22
        rp
  """
  return (rp - s11) / (s22 * (rp - s11) + s12s21)


def gamma_shifted(s11, s12s21, s22, r):
  """
  Name: vna.gamma_shifted()

  Args: s11
        s12s21
        s22
        r
  """
  return s11 + (s12s21*r / (1-s22*r))


def s1p_write(path_filename, freqs, gammas, file_format, Z0_str='R 50', force_dir=False):
  """
  Name: vna.s1p_write()

  Args: path_filename   - Full path to output file
        freqs           - array of frequencies where reflection coefficients are provided
        gammas          - complex array of reflection coefficient values
        file_format     - 0 = DB, 1 = MA, 2 = RI (2 default)
        Z0_str          - reference impedance to show in header ('R 50' default)
        force_dir       - If True, makes new directories as needed to match the provided path (False default)

  Desc: Writes the frequencies and reflection coefficients to an S1P formatted file.
  """
  
  if force_dir:
    # Make the directory path to the file
    dirs = os.path.dirname(path_filename)
    try:
      os.makedirs(dirs)

    # If the directory already exists, ignore the error.  But pass along
    # any other errors
    except OSError as exception:
      if exception.errno != errno.EEXIST:
        raise

  if file_format == 0:
    #DB format
    header = '# HZ S DB {}\n'.format(Z0_str)
    column1 = 20 * np.log10(np.absolute(gammas))
    column2 = np.angle(gammas, True) # degrees

  elif file_format == 1: 
    #MA format
    header = '# HZ S MA {}\n'.format(Z0_str)
    column1 = np.abs(gammas)
    column2 = np.angle(gammas, True) # degrees

  else: 
    #RI format
    header = '# HZ S RI {}\n'.format(Z0_str)
    column1 = np.real(gammas)
    column2 = np.imag(gammas)
    
  with open (path_filename, 'w') as writefile:

    writefile.write(header)

    for f, c1, c2 in zip(freqs, column1, column2):
      writefile.write('{}, {}, {}\n'.format(f, c1, c2))


def s1p_read(path_filename):
  """
  Name: vna.s1p_read()

  Args: path_filename

  Desc: Loads file and returns output of s1p_read_from_text
  """
  with open (path_filename, "r") as readfile:
    data = readfile.read()

  return s1p_read_from_text(data)
	

def s1p_read_from_text(text):
  """
  Name: vna.s1p_read()

  Args: text of an S1P formatted file

  Desc: Returns Gamma (complex) read from the text.
  """

  lines = text.split('\n')
  flag = None
  comment_rows = 0
	
  # Read through the comments at the top of the file
  for row in lines:
				
    # checking settings line
    if row[0] == '#':
      if ('DB' in row) or ('dB' in row):
        flag = 'DB'
				
      if 'MA' in row:
        flag = 'MA'
			
      if 'RI' in row:
        flag = 'RI'
				
    # counting number of lines commented out
    if ('#' in row) or ('!' in row):
      comment_rows += 1
    else:
      break
					
  # Load data
  d = np.genfromtxt(
        BytesIO(text), 
        skip_header=comment_rows)
  f = d[:,0]

  if flag == 'DB':
    r = db_to_r(d)

  if flag == 'MA':
    r = ma_to_r(d)

  if flag == 'RI':
    r = ri_to_r(d)

  return (r, f)
	

def db_to_r(d):
  """
  Name: vna.db_to_r()

  Args: d - 2D array with columns: S magnitude (dB), S phase (degrees)
  
  Desc: Converts the input array from S_Mag and S_phase to Gamma (complex)
  """
  return 10**(d[:,1]/20) * (np.cos((np.pi/180)*d[:,2]) + 1j*np.sin((np.pi/180)*d[:,2]))


def ma_to_r(d):
  """
  Name: vna.ma_to_r()

  Args: d - 2D array with columns: S magnitude (linear), S phase (degrees)
  
  Desc: Converts the input array from S_Mag and S_phase to Gamma (complex)
  """
  return d[:,1] * (np.cos((np.pi/180)*d[:,2]) + 1j*np.sin((np.pi/180)*d[:,2]))


def ri_to_r(d):
  """
  Name: vna.ri_to_r()

  Args: d - 2D array with columns: Gamma (real), Gamma (imaginary)
  
  Desc: Converts the input array from Gamma real and imaginary to Gamma (complex)
  """
  return d[:,1] + 1j*d[:,2]


def de_embed(r1a, r2a, r3a, r1m, r2m, r3m, rp):
  """
  Name: vna.de_embed()

  Args: r1a, 
        r2a, 
        r3a, 
        r1m, 
        r2m, 
        r3m, 
        rp
  
  Desc: This only works with 1D arrays, where each point in the array is
        a value at a given frequency.  The output is also a 1D array.
  """

  s11    = np.zeros(len(r1a)) + 0j   # 0j added to make array complex
  s12s21 = np.zeros(len(r1a)) + 0j
  s22    = np.zeros(len(r1a)) + 0j
	
  for i in range(len(r1a)):
    b = np.array([r1m[i], r2m[i], r3m[i]])#.reshape(-1,1)
    A = np.array([[1, r1a[i], r1a[i]*r1m[i]],
                  [1, r2a[i], r2a[i]*r2m[i]],
		              [1, r3a[i], r3a[i]*r3m[i]]])
    x = np.linalg.lstsq(A,b)[0]
    s11[i]    = x[0]
    s12s21[i] = x[1]+x[0]*x[2]
    s22[i]    = x[2]	
	
  r = gamma_de_embed(s11, s12s21, s22, rp)
	
  return r, s11, s12s21, s22


def fiducial_parameters_85033E(R, md):
  """
  Name: vna.fiducial_parameters_85033E

  Args: R
        md
  
  Desc: Returns the default open, short, load parameters for 85033E VNA.
  """

  # Parameters of open
  open_off_Zo     =  50 
  open_off_delay  =  29.243e-12
  open_off_loss   =  2.2*1e9
  open_C0 	=  49.43e-15 
  open_C1 	= -310.1e-27
  open_C2 	=  23.17e-36
  open_C3 	= -0.1597e-45

  op = np.array([open_off_Zo, open_off_delay, open_off_loss, open_C0, open_C1, open_C2, open_C3])

  # Parameters of short
  short_off_Zo    =  50 
  short_off_delay =  31.785e-12
  short_off_loss  =  2.36*1e9
  short_L0 	=  2.077e-12
  short_L1 	= -108.5e-24
  short_L2 	=  2.171e-33
  short_L3 	= -0.01e-42

  sp = np.array([short_off_Zo, short_off_delay, short_off_loss, short_L0, short_L1, short_L2, short_L3])

  # Parameters of match
  match_off_Zo    = 50

  if md == 0:
    match_off_delay = 0
  elif md == 1:
    match_off_delay = 30e-12   # rough average between open and short
  match_off_loss  = 2.3*1e9
  match_R         = R

  mp = np.array([match_off_Zo, match_off_delay, match_off_loss, match_R])

  return (op, sp, mp)


def standard_open(f, par):
  """
  Name: vna.standard_open()

  Args: f
        par
  
  Desc: 
  """

  offset_Zo    	= par[0]
  offset_delay 	= par[1]
  offset_loss  	= par[2]
  C0 		= par[3]
  C1 		= par[4]
  C2 		= par[5]
  C3 		= par[6]

  # Termination 
  Ct_open = C0 + C1*f + C2*f**2 + C3*f**3
  Zt_open = 0 - 1j/(2*np.pi*f*Ct_open)
  Rt_open = impedance2gamma(Zt_open,50)

  # Transmission line
  Zc_open  = (offset_Zo + (offset_loss/(2*2*np.pi*f))*np.sqrt(f/1e9)) - 1j*(offset_loss/(2*2*np.pi*f))*np.sqrt(f/1e9)
  temp     = ((offset_loss*offset_delay)/(2*offset_Zo))*np.sqrt(f/1e9)
  gl_open  = temp + 1j*( (2*np.pi*f)*offset_delay + temp )

  # Combined reflection coefficient
  R1      = impedance2gamma(Zc_open,50)
  ex      = np.exp(-2*gl_open)
  Rt      = Rt_open
  Ri_open = ( R1*(1 - ex - R1*Rt) + ex*Rt ) / ( 1 - R1*(ex*R1 + Rt*(1 - ex)) )

  return Ri_open
	

def standard_short(f, par):
  """
  Name: vna.standard_short()

  Args: f
        par
  
  Desc: 
  """

  offset_Zo    	= par[0]
  offset_delay 	= par[1]
  offset_loss  	= par[2]
  L0 		= par[3]
  L1 		= par[4]
  L2 		= par[5]
  L3 		= par[6]

  # Termination
  Lt_short = L0 + L1*f + L2*f**2 + L3*f**3
  Zt_short = 0 + 1j*2*np.pi*f*Lt_short
  Rt_short = impedance2gamma(Zt_short,50)

  # Transmission line
  Zc_short = (offset_Zo + (offset_loss/(2*2*np.pi*f))*np.sqrt(f/1e9)) - 1j*(offset_loss/(2*2*np.pi*f))*np.sqrt(f/1e9)
  temp     = ((offset_loss*offset_delay)/(2*offset_Zo))*np.sqrt(f/1e9)
  gl_short = temp + 1j*( (2*np.pi*f)*offset_delay + temp )

  # Combined reflection coefficient
  R1       = impedance2gamma(Zc_short,50)
  ex       = np.exp(-2*gl_short)
  Rt       = Rt_short
  Ri_short = ( R1*(1 - ex - R1*Rt) + ex*Rt ) / ( 1 - R1*(ex*R1 + Rt*(1 - ex)) )

  return Ri_short


def standard_match(f, par):
  """
  Name: vna.standard_match()

  Args: f
        par
  
  Desc: 
  """

  offset_Zo    = par[0]
  offset_delay = par[1]
  offset_loss  = par[2]
  Resistance   = par[3]

  # Termination	
  Zt_match = Resistance
  Rt_match = impedance2gamma(Zt_match,50)

  # Transmission line
  Zc_match = (offset_Zo + (offset_loss/(2*2*np.pi*f))*np.sqrt(f/1e9)) - 1j*(offset_loss/(2*2*np.pi*f))*np.sqrt(f/1e9)
  temp     = ((offset_loss*offset_delay)/(2*offset_Zo))*np.sqrt(f/1e9)
  gl_match = temp + 1j*( (2*np.pi*f)*offset_delay + temp )

  # combined reflection coefficient %%%%
  R1       = impedance2gamma(Zc_match,50)
  ex       = np.exp(-2*gl_match)
  Rt       = Rt_match
  Ri_match = ( R1*(1 - ex - R1*Rt) + ex*Rt ) / ( 1 - R1*(ex*R1 + Rt*(1 - ex)) )

  return Ri_match


def agilent_85033E(f, resistance_of_match, md):
  """
  Name: vna.agilent_85033E()

  Args: f
        resistance_of_match
        md

  Desc: 
  """
  op, sp, mp = fiducial_parameters_85033E(resistance_of_match, md)
  o = standard_open(f, op)
  s = standard_short(f, sp)
  m = standard_match(f, mp)

  return (o, s, m)


def internal_s11_correction(oi, si, li, ai):
  """
  Name: vna.internal_s11_correction()

  Args: oi  - S11 trace for open standard [Gamma (complex)]
        si  - S11 trace for short standard [Gamma (complex)]
        li  - S11 trace for load (match) standard [Gamma (complex)]
        ai  - S11 trace that will be calibrated for device (antenna) under test [Gamma (complex)]

  Desc: Corrects for the antenna S11 using the internal OLS standards.  All traces 
        should be evaluated at the same frequencies.  

  Returns the calibrated DUT trace as Gamma (complex)  
  """
  nfreqs = len(oi)

  # reflection references
  oref =  1*np.ones(nfreqs)
  sref = -1*np.ones(nfreqs)
  lref =  0*np.ones(nfreqs)

  # apply calibration
  aic  = de_embed(oref, sref, lref, oi, si, li, ai)

  return aic[0]


def external_s11_correction(f, ant_s11, f_m, o_sw_m, s_sw_m, l_sw_m, o_ex, s_ex, l_ex, resistance_of_match, f_norm=75e6, N_poly_terms=10):  
  """
  Name: vna.external_s11_correction()

  Args: f                     - array/list of frequencies for ant_s11 (Hz)
        ant_s11               - complex numpy array containing measured antenna S11 that has 
                                already been corrected by the internal OLS standards
        f_m                   - array/list of frequencies for the internal and external calibration S11 traces
        o_sw_m                - complex numpy array containing measured internal open S11 at time of external calibration
        s_sw_m                - complex numpy array containing measured internal short S11 at time of external calibration
        l_sw_m                - complex numpy array containing measured internal load/match S11 at time of external calibration
        o_ex                  - complex numpy array containing measured external open S11
        s_ex                  - complex numpy array containing measured external short S11
        l_ex                  - complex numpy array containing measured internal load/match S11
        resistance_of_match   - resistance of external match (Ohm)
        f_norm                - normalization frequency for polynomial fits
        N_poly_terms          - number of terms for polynomial fits

  Desc: Corrects for the receiver antenna switch path by using measurements of OLS standards 
        connected to the front of the receiver.  All traces should be evaluated at the same 
        frequencies.  

  Returns the calibrated DUT trace as Gamma (complex) 
  """

  # Standards assumed at the switch
  o_sw =  1 * np.ones(len(f_m))
  s_sw = -1 * np.ones(len(f_m))
  l_sw =  0 * np.ones(len(f_m))	

  # Correction at the switch
  o_ex_c, xx1, xx2, xx3 = de_embed(o_sw, s_sw, l_sw, o_sw_m, s_sw_m, l_sw_m, o_ex)
  s_ex_c, xx1, xx2, xx3 = de_embed(o_sw, s_sw, l_sw, o_sw_m, s_sw_m, l_sw_m, s_ex)
  l_ex_c, xx1, xx2, xx3 = de_embed(o_sw, s_sw, l_sw, o_sw_m, s_sw_m, l_sw_m, l_ex)

  # Computation of S-parameters to the receiver input
  md = 1
  oa, sa, la = agilent_85033E(f_m, resistance_of_match, md)
  xx, s11, s12s21, s22 = de_embed(oa, sa, la, o_ex_c, s_ex_c, l_ex_c, o_ex_c)

  # Polynomial fit of S-parameters from "f" to output frequency vector "f_out"
  # --------------------------------------------------------------------------

  # Frequency normalization
  fn = f_m / f_norm
  fn_in = f / f_norm	

  # Real-Imaginary parts
  real_s11    = np.real(s11)
  imag_s11    = np.imag(s11)
  real_s12s21 = np.real(s12s21)
  imag_s12s21 = np.imag(s12s21)
  real_s22    = np.real(s22)
  imag_s22    = np.imag(s22)

  # Polynomial fits
  p = np.polyfit(fn, real_s11, N_poly_terms-1)
  fit_real_s11 = np.polyval(p, fn_in)

  p = np.polyfit(fn, imag_s11, N_poly_terms-1)
  fit_imag_s11 = np.polyval(p, fn_in)

  p = np.polyfit(fn, real_s12s21, N_poly_terms-1)
  fit_real_s12s21 = np.polyval(p, fn_in)

  p = np.polyfit(fn, imag_s12s21, N_poly_terms-1)
  fit_imag_s12s21 = np.polyval(p, fn_in)

  p = np.polyfit(fn, real_s22, N_poly_terms-1)
  fit_real_s22 = np.polyval(p, fn_in)

  p = np.polyfit(fn, imag_s22, N_poly_terms-1)
  fit_imag_s22 = np.polyval(p, fn_in)

  fit_s11    = fit_real_s11    + 1j*fit_imag_s11
  fit_s12s21 = fit_real_s12s21 + 1j*fit_imag_s12s21
  fit_s22    = fit_real_s22    + 1j*fit_imag_s22

  # Corrected antenna S11
  corr_ant_s11 = gamma_de_embed(fit_s11, fit_s12s21, fit_s22, ant_s11)

  return (corr_ant_s11, fit_s11, fit_s12s21, fit_s22)





