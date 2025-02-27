# fm.py
# Some code to try to convert dx7 patches into AMY commands
# Use the dx7 module if you want to A/B test AMY's FM mode against a dx7 emulation.
# AMY is not a dx7 emulator, so it's not going to be perfect or even close, especially for some of the weirder modes of the dx7
# but fun to play with!
# Get the dx7 module from https://github.com/bwhitman/learnfm
import alles, dx7
import numpy as np
import time



# Use learnfm's dx7 to render a dx7 note from MSFA
def dx7_render(patch_number, midinote, velocity, samples, keyup_sample):
	s = dx7.render(patch_number, midinote, velocity, samples, keyup_sample)
	return np.array(s)/32767.0

def play(patch):
    alles.reset()
    setup_patch(decode_patch(get_patch(patch)))
    alles.send(osc=6,vel=1,note=40,bp0_target=alles.TARGET_AMP,bp0="0,1,500,0,500,0")
    time.sleep(0.5)
    alles.send(osc=6,vel=0)
    time.sleep(0.5)
    alles.send(osc=6,vel=1,note=50)
    time.sleep(0.5)
    alles.send(osc=6,vel=1,note=51)
    time.sleep(0.5)
    alles.send(osc=6,vel=1,note=52)
    time.sleep(0.5)
    alles.send(osc=6,vel=1,note=40,bp0_target=alles.TARGET_AMP,bp0="0,1,100,0,0,0")
    time.sleep(0.25)
    alles.send(osc=6,vel=0)

def setup_patch(p):
	# Take a FM patch and output AMY commands to set up the patch. Send alles.send(vel=0,osc=6,note=50) after
    # Problem here, pitch values are such that 0 = -n octave, 99 = + n octave 
    # pitch level = 50 means no change (or 1 for us)
    # can our breakpoints handle negative numbers? 
    alles.reset()
    print(p["name"])
    pitch_rates, pitch_times = p["bp_pitch_rates"], p["bp_pitch_times"]
    pitchbp = "%d,%f,%d,%f,%d,%f,%d,%f" % (
        pitch_times[0], pitch_rates[0], pitch_times[1], pitch_rates[1], pitch_times[2], pitch_rates[2], pitch_times[3], pitch_rates[3]
    )
	# Set up each operator
    for i,op in enumerate(p["ops"]):
        freq_ratio = -1
        freq = -1
        # Set the ratio or the fixed freq
        if(op.get("fixedhz",None) is not None):
            freq = op["fixedhz"]
        else:
            freq_ratio = op["ratio"]
        bp_rates, bp_times = op["bp_opamp_rates"], op["bp_opamp_times"]
        opbp = "%d,%f,%d,%f,%d,%f,%d,%f" % (
            bp_times[0], bp_rates[0], bp_times[1], bp_rates[1], bp_times[2], bp_rates[2], bp_times[3], bp_rates[3]
        )
        #print("osc %d (op %d) freq %f ratio %f beta-bp %s pitch-bp %s beta %f detune %d" % (i, (i-6)*-1, freq, freq_ratio, opbp, pitchbp, op["opamp"], op["detunehz"]))
        if(freq>=0):
            alles.send(osc=i, freq=freq, ratio=freq_ratio,bp0_target=alles.TARGET_AMP+alles.TARGET_LINEAR,bp0=opbp, bp1=pitchbp, bp1_target=alles.TARGET_FREQ+alles.TARGET_LINEAR, amp=op["opamp"], detune=op["detunehz"])
        else:
            alles.send(osc=i, freq=freq, ratio=freq_ratio,bp0_target=alles.TARGET_AMP+alles.TARGET_LINEAR,bp0=opbp, amp=op["opamp"], detune=op["detunehz"])

    # Set up the main carrier note
    lfo_target = 0
    # Choose the bigger one
    if(p.get("lfoampmoddepth",0) + p.get("lfopitchmoddepth",0) > 0):
        if(p.get("lfoampmoddepth",0) >= p.get("lfopitchmoddepth",0)):
            lfo_target=alles.TARGET_AMP
            lfo_amp = output_level_to_amp(p.get("lfoampmoddepth",0))
        else:
            lfo_target=alles.TARGET_FREQ
            lfo_amp = output_level_to_amp(p.get("lfopitchmoddepth",0))

    if(lfo_target>0):
        alles.send(osc=7, wave=p["lfowaveform"],freq=p["lfospeed"], amp=lfo_amp)
        alles.send(osc=6,lfo_target=lfo_target, lfo_source=7)
        #print("osc 7 lfo wave %d freq %f amp %f target %d" % (p["lfowaveform"],p["lfospeed"], lfo_amp, lfo_target))
    print("osc 6 (main)  algo %d feedback %f pitchenv %s" % ( p["algo"], p["feedback"], pitchbp))
    alles.send(osc=6, wave=alles.ALGO, algorithm=p["algo"], feedback=p["feedback"], algo_source="0,1,2,3,4,5", bp1=pitchbp, bp1_target=alles.TARGET_FREQ+alles.TARGET_LINEAR)

# spit out all the params of a patch for a header file
def header_patch(p):
    os  = []
    for i,op in enumerate(p["ops"]):
        freq_ratio = -1
        freq = -1
        if(op.get("fixedhz",None) is not None):
            freq = op["fixedhz"]
        else:
            freq_ratio = op["ratio"]
        o_data = [freq, freq_ratio, op["opamp"], op["bp_opamp_rates"], op["bp_opamp_times"],op["detunehz"]]
        os.append(o_data)
    lfo_target , lfo_freq, lfo_wave, lfo_amp, = (-1, -1, -1, -1)
    # Choose the bigger one
    if(p.get("lfoampmoddepth",0) + p.get("lfopitchmoddepth",0) > 0):
        lfo_freq = p["lfospeed"]
        lfo_wave = p["lfowaveform"]
        if(p.get("lfoampmoddepth",0) >= p.get("lfopitchmoddepth",0)):
            lfo_target=alles.TARGET_AMP
            lfo_amp = output_level_to_amp(p.get("lfoampmoddepth",0))
        else:
            lfo_target=alles.TARGET_FREQ
            lfo_amp = output_level_to_amp(p.get("lfopitchmoddepth",0))
    return (p["name"], p["algo"], p["feedback"], p["bp_pitch_rates"], p["bp_pitch_times"], lfo_freq, lfo_wave, lfo_amp, lfo_target, os)

def generate_fm_header(patches, **kwargs):
    # given a list of patch numbers, output a fm.h
    out = open("main/amy/fm.h", "w")
    out.write("// Automatically generated by fm.generate_fm_header()\n#ifndef __FM_H\n#define __FM_H\n#define ALGO_PATCHES %d\n" % (len(patches)))
    all_patches = []
    ids = []
    for patch in patches:
        ids.append(patch)
        p = header_patch(decode_patch(get_patch(patch)))
        all_patches.append(p)

    out.write("const algorithms_parameters_t fm_patches[ALGO_PATCHES] = {\n")
    for idx,p in enumerate(all_patches):
        out.write("\t{ %d, %f, {%f, %f, %f, %f}, {%d, %d, %d, %d}, %f, %d, %f, %d, {\n" % 
            (p[1], p[2], p[3][0], p[3][1], p[3][2], p[3][3], p[4][0], p[4][1], p[4][2], p[4][3], p[5], p[6], p[7], p[8]))
        for i in range(6):
            out.write("\t\t\t{%f, %f, %f, {%f, %f, %f, %f}, {%d, %d, %d, %d}, %f}, /* op %d */\n" % 
                (p[9][i][0], p[9][i][1], p[9][i][2], p[9][i][3][0], p[9][i][3][1], p[9][i][3][2], p[9][i][3][3], 
                    p[9][i][4][0], p[9][i][4][1], p[9][i][4][2], p[9][i][4][3], p[9][i][5], (i-6)*-1 ))
        out.write("\t\t},\n\t}, /* %s (%d) */ \n" % (p[0], ids[idx]))
    out.write("};\n#endif // __FM_H\n")
    out.close()

def plot(us, them):
	import matplotlib.pyplot as plt
	fig, (s0,s1) = plt.subplots(2,1)
	s0.specgram(us_samples, NFFT=512, Fs=alles.SAMPLE_RATE)
	s1.specgram(them_samples, NFFT=512, Fs=alles.SAMPLE_RATE)
	fig.show()

# Play our version vs the MSFA version to A/B test
def play_patch(patch_number, midinote=50, length_s = 2, keyup_s = 1):
	dx7_patch = dx7.unpack(patch_number)
	p = decode_patch(dx7_patch)
	print(str(p["name"]))
	setup_patch(p,midinote)

	alles.note_on(osc=6,vel=4)
	us_samples0 = alles.render(keyup_s)
	alles.note_off(osc=6)
	us_samples1 = alles.render(length_s - keyup_s)
	us_samples = np.hstack((us_samples0, us_samples1))

	them_samples = dx7_render(patch_number, midinote, 90, int(length_s*alles.SAMPLE_RATE),int(keyup_s*alles.SAMPLE_RATE))

	# Uncomment this to show a spectra
	#plot(us_samples, them_samples)

	print("AMY:")
	alles.play(us_samples)
	time.sleep(length_s)

	# A/B against MSFA 
	time.sleep(0.25)
	print("MSFA:")
	alles.play(them_samples)
	time.sleep(length_s)
	return p

def output_level_to_amp(byte):
	# Sure could be a exp curve but seems a bit custom
	# https://i.stack.imgur.com/1FQqR.jpg
	"""
	From Dan:
		When doing phase modulation in LUTs, there’s the factor of lut_size (the difference between 
		phase and scaled_phase).  So 0.2 in the “phase” domain becomes 51.2 if we scale it up for a 256 pt LUT
	"""
	if(byte<20): return 0
	if(byte<40): return 0.1/14
	if(byte<50): return 0.25/14
	if(byte<60): return 0.5/14
	if(byte<70): return 1.2/14
	if(byte<80): return 2.75/14
	if(byte<85): return 4./14
	if(byte<90): return 6./14
	if(byte<88): return 6.05/14
	if(byte<89): return 6.1/14
	if(byte<90): return 6.2/14
	if(byte<91): return 6.5/14
	if(byte<92): return 7./14
	if(byte<93): return 8./14
	if(byte<94): return 9./14
	if(byte<95): return 9.5/14
	if(byte<96): return 10./14
	if(byte<97): return 11./14
	if(byte<98): return 12.5/14
	if(byte<99): return 13./14
	return 1.0

def get_patch(patch_number):
	# returns a patch (as in patches.h) from 
    # unpacked.bin generated by dx7db, see https://github.com/bwhitman/learnfm
    f = bytes(open("unpacked.bin", mode="rb").read())
    patch_data = f[patch_number*156:patch_number*156+156]
    #name = ''.join([i if (ord(i) < 128 and ord(i) > 31) else ' ' for i in str(patch_data[145:155])])
    return patch_data

# Given a patch byte stream, return a json object that describes it
def decode_patch(p):
	# This is likely incorrect, but an ok start
	def rate_to_ms(rate):
		"""
			"It may take over half a minute to reach level 1, depending on the setting of RATE 1 (R1)."
		"""
		# From MSFA. This is likely in samples to advance per sample?
		ratetab = [
			1, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12,
			12, 13, 13, 14, 14, 15, 16, 16, 17, 18, 18, 19, 20, 21, 22, 23, 24,
			25, 26, 27, 28, 30, 31, 33, 34, 36, 37, 38, 39, 41, 42, 44, 46, 47,
			49, 51, 53, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 79, 82,
			85, 88, 91, 94, 98, 102, 106, 110, 115, 120, 125, 130, 135, 141, 147,
			153, 159, 165, 171, 178, 185, 193, 202, 211, 232, 243, 254, 255]
		# This must be exp scaled so that 0 is 30 seconds, 1 is 10 seconds, 2 is 1 second, etc .. 
		# I don't know what i'm doing here, need help with this bit 
		return 180000. / (ratetab[rate]*64.0)

	def eg_to_bp(egrate, eglevel):
		# http://www.audiocentralmagazine.com/wp-content/uploads/2012/04/dx7-envelope.png
		# or https://yamahasynth.com/images/RefaceSynthBasics/EG_RatesLevels.png
		# rate seems to be "speed", so higher rate == less time
		# level is probably exp, but so is our ADSR? 
		#print ("Input rate %s level %s" %(egrate, eglevel))
		times = [0,0,0,0]
		rates = [0,0,0,0]

		total_ms = 0
		for i in range(4):
			ms = rate_to_ms(egrate[i])
			l = eglevel[i] / 99.0
			if(i!=3):
				total_ms = total_ms + ms
				times[i] = total_ms
				rates[i] = l
			else:
				# Release ms counter happens separately, so don't add
				times[i] = ms
				rates[i] = l
		return (rates, times)

	def eg_to_bp_pitch(egrate, eglevel):

		# http://www.audiocentralmagazine.com/wp-content/uploads/2012/04/dx7-envelope.png
		# or https://yamahasynth.com/images/RefaceSynthBasics/EG_RatesLevels.png
		# rate seems to be "speed", so higher rate == less time
		# level is probably exp, but so is our ADSR? 
		#print ("pitch Input rate %s level %s" %(egrate, eglevel))
		times = [0,0,0,0]
		rates = [1,0,0,0]
		total_ms = 0
		for i in range(4):
			ms = rate_to_ms(egrate[i])
			l = eglevel[i] / 50.0
			if(i!=3):
				total_ms = total_ms + ms
				times[i] = total_ms
				rates[i] = l
			else:
				# Release ms counter happens separately, so don't add
				times[i] = ms
				rates[i] = l
		return (rates, times)

	def lfo_speed_to_hz(byte):
		# https://www.yamahasynth.com/ask-a-question/generating-specific-lfo-frequencies-on-dx
		return [0.026, 0.042, 0.084, 0.126, 0.168, 0.210, 0.252, 0.294, 0.336, 0.372, 0.412, 0.456, 0.505, 0.542,
		 0.583, 0.626, 0.673, 0.711, 0.752, 0.795, 0.841, 0.880, 0.921, 0.964, 1.009, 1.049, 1.090, 1.133,
		 1.178, 1.218, 1.259, 1.301, 1.345, 1.386, 1.427, 1.470, 1.514, 1.554, 1.596, 1.638, 1.681, 1.722,
		 1.764, 1.807, 1.851, 1.932, 1.975, 2.018, 2.059, 2.101, 2.143, 2.187, 2.227, 2.269, 2.311, 2.354,
		 2.395,2.437,2.480,2.523,2.564,2.606,2.648,2.691,2.772,2.854,2.940,3.028,3.108,3.191,3.275,3.362,3.444,3.528,
		 3.613,3.701,3.858,4.023,4.194,4.372,4.532,4.698,4.870,5.048,5.206,5.369,5.537,5.711,6.024,6.353,6.701,7.067,
		 7.381,7.709,8.051,8.409,8.727,9.057,9.400,9.756,10.291,10.855,11.450,12.077,12.710,13.376,14.077,14.815,15.440,
		 16.249,17.100,17.476,18.538,19.663,20.857,22.124,23.338,24.620,25.971,27.397,28.902,30.303,31.646,33.003,34.364,
		 37.037,39.682][byte]


	def lfo_wave(byte):
		if(byte == 0): return alles.TRIANGLE
		if(byte == 1): return alles.TRIANGLE # saw down TODO
		if(byte == 2): return alles.TRIANGLE # up, TODO 
		if(byte == 3): return alles.PULSE 
		if(byte == 4): return alles.SINE
		if(byte == 5): return alles.NOISE
		return None

	def curve(byte):
		# What is this curve for? Pi
		if(byte==0): return "-lin"
		if(byte==1): return "-exp"
		if(byte==2): return "+exp"
		if(byte==3): return "+lin"
		return "unknown"

	def coarse_fine_fixed_hz(coarse, fine):
		# so many are > 3 (7500 out of 38K.) msfa cuts it like this, not sure whats' up here. maybe the knob loops over? 
		#print("fixed coarse %d fine %d" % (coarse, fine))
		coarse = coarse & 3 
		if(coarse==0):
			return 1 + ((fine / 10.0) )
		if(coarse==1):
			return 10 + (fine  )
		if(coarse==2):
			return 100 + ((fine * 10) )
		if(coarse==3):
			return 1000 + ((fine * 100.0) )
		#print("fixed coarse > 3, is %d" % (coarse))
		return 0

	def coarse_fine_ratio(coarse,fine):
		#print("ratio coarse %d fine %d" % (coarse, fine))

		if(coarse==0):
			return 0.5 + ((fine/200.0) )
		coarse = coarse & 31 # see above
		return coarse + (fine/100.0)
		

	patch = {}
	ops = []
	# Starts at op 6
	c = 0
	for i in range(6):
		op = {}
		op["rate"] = [x for x in p[c:c+4]]
		op["level"] =  [x for x in p[c+4:c+8]]
		# TODO, this should be computed after scaling 
		(op["bp_opamp_rates"], op["bp_opamp_times"]) = eg_to_bp([x for x in p[c:c+4]], [x for x in p[c+4:c+8]])
		c = c + 8
		op["breakpoint"] = p[c]
		c = c + 1
		# left depth, right depth -- this + the curve scales the op rates left and right of note # specified in breakpoint
		op["bp_depths"] = [p[c], p[c+1]]
		c = c + 2
		# curve type (l , r)
		op["bp_curves"] = [curve(p[c]), curve(p[c+1])]
		c = c + 2
		op["kbdratescaling"] = p[c]
		c = c + 1
		op["ampmodsens"] = p[c]
		c = c + 1
		op["keyvelsens"] = p[c]
		c = c + 1
		op["opamp"] = output_level_to_amp(p[c])
		c = c + 1
		if(p[c] == 1): # fixed
			op["fixedhz"] = coarse_fine_fixed_hz(p[c+1], p[c+2])
		else:
			op["ratio"] = coarse_fine_ratio(p[c+1], p[c+2])
		op["coarse"] = p[c+1]
		op["fine"] = p[c+2]
		c = c + 3
		op["detunehz"] = p[c]
		c = c + 1
		ops.append(op)

	patch["ops"] = ops

	(patch["bp_pitch_rates"], patch["bp_pitch_times"]) = eg_to_bp_pitch([x for x in p[c:c+4]], [x for x in p[c+4:c+8]])
	c = c + 8
	patch["algo"] = p[c] # ours start at 0
	c = c + 1
	patch["feedback"] = p[c]/14.0
	c = c + 1
	patch["oscsync"] = p[c]
	c = c + 1
	patch["lfospeed"] = lfo_speed_to_hz(p[c])
	c = c + 1
	patch["lfodelay"] = p[c]
	c = c + 1
	patch["lfopitchmoddepth"] = p[c]
	c = c + 1
	patch["lfoampmoddepth"] = p[c]
	c = c + 1
	patch["lfosync"] = p[c]
	c = c + 1
	patch["lfowaveform"] = lfo_wave(p[c])
	c = c + 1
	patch["pitchmodsens"] = p[c]
	c = c + 1
	patch["transpose"] = p[c]
	c = c + 1
	patch["name"] =  ''.join(chr(i) for i in p[c:c+10])
	c = c + 10
	return patch



