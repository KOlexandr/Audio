import math
import numpy
import scipy
from numpy.ma.core import sort
from numpy.core.umath import sign
from numpy.matlib import repmat, rand
from numpy.core.fromnumeric import mean
from numpy.lib.arraysetops import setxor1d

from beans.WavFile import WavFile
from variables import path_to_hmm_words

__author__ = 'Olexandr'


def resample(x, ratio, quality='sinc_medium', window=None, algorithm='scikits'):
    """
    Resamples signal column-wise.
    By default will try to use scikits.samplerate.resample if available.
    Otherwise will use scipy.signal.resample.

      ratio: A float value indicating ratio for resampling
    quality: A quality string to be passed to scikits.samplerate.resample.
             Useful quality values include sinc_medium, sinc_fastest, sinc_best.
             This value is ignored by the scipy algorithm
     window: A window to be passed to scipy.signal.resample. Default is None.
             This value is ignored by the scikits algorithm.
       algo: The algorithm to be used, either 'scipy' or 'scikits'. Default is 'scikits'
    """
    #decide which function we will use
    func = lambda data: data
    if algorithm == 'scikits':
        try:
            import scikits.samplerate
            func = lambda array, r, q, w: scikits.samplerate.resample(array, r, q)
        except ImportError:
            print("Cannot find scikits.samplerate. Resampling using scipy.signal.resample")
            algorithm = 'scipy'
    if algorithm == 'scipy':
        import scipy.signal
        func = lambda array, r, q, w: scipy.signal.resample(array, int(round(len(array) * r)), window=w)
    if func is None:
        raise ValueError("Unknown algo %s. Use either scikits or scipy" % algorithm)

    #call function over columns of array
    if len(x.shape) == 1 or x.shape[1] == 1:
        y = func(x, ratio, quality, window)
    else:
        y = numpy.array([])
        for i in range(x.shape[1]):
            y = numpy.concatenate((y, func(x[:, i], ratio, quality, window)))
        y = y.reshape(x.shape[1], -1).T
    return y


def get_ceps(wav_path, frame_rate, a, b, resample_flag=True):
    """
    Function getceps.m for computing cepstral coefficients
    Returns the cepstral coefficients in an array
    Returns the a: b coefficients (13 coefficients in total)

    @param wav_path: path to wav file
    @param frame_rate: frame rate (WavFile.sample_rate)
    @param a: start index
    @param b: end index
    """
    wav = WavFile(wav_path)
    x = wav.get_one_channel_data(False)
    if resample_flag:
        x = list(resample(x, wav.frame_rate / 8000))
    mfcc_array = mfcc(x, 8000, frame_rate)
    return numpy.transpose(mfcc_array)[:, a:b]


def max_n(x, n=None):
    """
    This function returns the N maximum values of vector X  with their indices.
    V is  a vector which has the maximum values, and I is the index matrix,
    i.e.  indices corresponding to N maximum values in vector X
    """
    if n is None:
        # Only the first maximum (default n=1)
        max_val = max(x)
        return max_val, x.index(max_val)
    else:
        n = min(len(x), n)
        tmp = list(x)
        v = sort(x)
        idx = list(map(lambda z: tmp.index(z), v))
        res_v = [v[i] for i in range(len(x)-1, len(x)-n-1, -1)]
        res_idx = [idx[i] for i in range(len(x)-1, len(x)-n-1, -1)]
    return res_v, res_idx


def mfcc(input_vector, sampling_rate=16000, frame_rate=100):
    """
    Function on Mel frequency cepstrum coefficient (MFCC)
    Adapted from the MFCC code in Auditory Toolbox, 1998

    @param input_vector: vector of audio data (always list or ndArray 1 x len() size)
    l_filters = linear_filters
    t_filters = total_filters
    t_h = triangle_height
    """

    input_vector = list(input_vector)
    # enter auditory filter bank parameters below
    lowest_frequency, log_spacing, linear_spacing = 133.3333, 1.0711703, 66.66666666
    log_filters, l_filters, fft_size, cepstral_coefficients, window_size = 27, 13, 512, 13, 256

    t_filters = l_filters + log_filters
    freq = list(map(lambda x: x * linear_spacing + lowest_frequency, range(l_filters)))
    freq[l_filters:t_filters + 1] = list(
        map(lambda x: freq[l_filters - 1] * log_spacing ** x, range(1, log_filters + 3)))
    lower, center, upper = freq[0:t_filters], freq[1:t_filters + 1], freq[2:t_filters + 2]

    # combine FFT bins with triangular weighting functions defined below
    mfcc_filter_weights = numpy.zeros((t_filters, fft_size))

    t_h = [2.0 / (i - j) for i, j in zip(upper, lower)]
    fft_frequencies = list(map(lambda x: x / fft_size * sampling_rate, range(fft_size)))
    for chan in range(t_filters):
        f1 = [1 if lower[chan] < i <= center[chan] else 0 for i in fft_frequencies]
        f1_t_h = list(map(lambda x: t_h[chan] * x, f1))
        freq_l_c_l = list(map(lambda x: ((x - lower[chan]) / (center[chan] - lower[chan])), fft_frequencies))
        part1 = [i * j for i, j in zip(f1_t_h, freq_l_c_l)]

        f2 = [1 if center[chan] < i < upper[chan] else 0 for i in fft_frequencies]
        f2_t_h = list(map(lambda x: t_h[chan] * x, f2))
        freq_u_u_c = list(map(lambda x: ((upper[chan] - x) / (upper[chan] - center[chan])), fft_frequencies))
        part2 = [i * j for i, j in zip(f2_t_h, freq_u_u_c)]

        mfcc_filter_weights[chan] = [i + j for i, j in zip(part1, part2)]

    # define Hamming window function
    ham_window = [0.54 - 0.46 * math.cos(2 * math.pi * i / window_size) for i in range(window_size)]

    # define DCT matrix
    mfcc_dct_matrix = numpy.dot(numpy.reshape(range(cepstral_coefficients), (cepstral_coefficients, 1)),
                                numpy.reshape([(2 * j + 1) * math.pi / 2 / t_filters for j in range(t_filters)],
                                              (1, t_filters)))
    for i in range(len(mfcc_dct_matrix)):
        for j in range(len(mfcc_dct_matrix[i])):
            mfcc_dct_matrix[i][j] = 1 / math.sqrt(t_filters / 2) * math.cos(mfcc_dct_matrix[i][j])

    mfcc_dct_matrix[0, :] = list(map(lambda x: x * math.sqrt(2) / 2, mfcc_dct_matrix[0, :]))
    # define preemphasis high pass fiter to enhance signal
    pre_emphasized = list(map(lambda x: x * 0.03, input_vector))
    # allocate space jor output
    window_step = sampling_rate / frame_rate
    step = (len(input_vector) - window_size) / window_step
    cols = int(math.floor(abs(step)) * sign(step))
    if cols <= 0:
        return None
    ceps = numpy.zeros((cepstral_coefficients, cols))
    # Compute MFCC coefficients below:
    # 1. Hamming window the data, pre-emphasis
    # 2. FFT, auditory filter bank then take log
    # 3. project to DCT basis vectors for dimensional reduction.
    for start in range(cols):
        first = int(start * window_step)
        last = int(first + window_size)
        fft_data = [0] * fft_size
        fft_data[0:window_size] = [x * w for x, w in zip(pre_emphasized[first:last], ham_window)]
        fft_mag = abs(numpy.fft.fft(fft_data))
        ear_mag = list(map(math.log10, list(numpy.dot(mfcc_filter_weights, numpy.transpose(fft_mag)))))
        ceps[:, start] = numpy.dot(mfcc_dct_matrix, ear_mag)
    return ceps


def vq_index(x_in, cb_in):
    """
    Distance function
    Returns the closest index of vectors in X  to  codewords in CB
    indexes is a vector.  The len ofI  is equal to  the number of columns in X
    Each element ofI  is the index of closest codeword (column) of CB to
    corresponding column of X
    """
    l_size = len(cb_in)
    n_size = x_in.shape[1]
    d = numpy.zeros((l_size, n_size))
    if l_size * n_size < 64 * 10000:
        for i in range(l_size):
            tmp = []
            for j in range(n_size):
                tmp.append(cb_in[i])
            tmp = numpy.transpose(tmp)
            for j in range(tmp.shape[1]):
                d[i, j] = sum([(k - h)**2 for k, h in zip(tmp[:, j], x_in[:, j])])
        dst, indexes = [], []
        for j in range(d.shape[1]):
            dst.append(min(d[:, j]))
            indexes.append(list(d[:, j]).index(dst[j]))
    else:
        raise Exception("Too big size of data")
    return indexes, dst


#======================================================
def size(array, dem=None):
    array = list(array)
    if dem is None or dem == 2:
        return len(array), len(array[0]) if type(array[0]) == list else 1
    elif dem == 1:
        s = 0
        for k in array:
            s += len(k) if type(array[0]) == list else 0
        return s
    return None


def encode(cep_set, cbk):
    """
    Function encode.m for VQ-encoding
    Encode ceps into an index sequence using code book cbk
    idx _out - encoded index sequence
    cepset - ceps cell set (could be multiple subjects for multiple digits)
    cbk - code_book
    single_flag - single set flag
    """
    n_set = len(cep_set)
    n_code = numpy.rank(cbk)
    idx_out = []
    for m in range(n_set):
        nr = size(cep_set[m], 1)
        idx = []
        for i in range(nr):
            dist = []
            for j in range(n_code):
                tmp = [i - j for i, j in (cep_set[m][i, :], cbk[j, :])]
                dist.append(list(map(lambda y: y / sum(tmp), tmp)))
            idx = dist.index(min(dist))
        idx_out.append(idx)
    return idx_out


def drecm(seqs, hmm_link, hmm_pb):
    # Function drecm.mfor maximum score (mx) of a symbol sequence and recognition 
    # uses Viterbi algorithm to search for the best matched state sequence oft he input 
    # observation sequence (seqs)  in 
    # trained HMM models (hmm_link,hmm_pb) of digits. 
    nobs = len(seqs)
    n_state = size(hmm_link, 1)
    # Model training to  be consistent with model reading 
    hmm_link = numpy.transpose(hmm_link)
    hmm_pb = numpy.transpose(hmm_pb)
    large = 1e37
    epsilon = 1e-6
    alpha = numpy.zeros(n_state, 2)
    prev = numpy.zeros(nobs, n_state)
    alpha[0:n_state, 0] = -large
    alpha[0, 0] = math.log(1 + hmm_pb[seqs[0], 0])
    # forward computing
    index = -1
    for t in range(1, nobs):
        for i in range(n_state):
            mx = -large
            for j in range(i):
                if hmm_link[i, j] >= epsilon:
                    sumpr = alpha[j, 0] + math.log(1 + hmm_link[i, j])
                    if sumpr > mx:
                        mx = sumpr
                        index = j
            alpha[i, 1] = mx + math.log(1 + hmm_pb[seqs[t], i])
            prev[t, i] = index
        # updating
        alpha[0:n_state, 0] = alpha[0:n_state, 1]
    # back tracing
    mx = 0.0
    for i in range(n_state):
        if alpha[i, 0] > mx:
            mx = alpha[i, 0]
    return mx


def vq_split(x, code_book_size=32):
    """
    Function vq_split.m for VQ and K-Means Algorithm with Splitting for Training
    # Inputs: 
    # @param x: a matrix each column of which is a data vector
    # @param code_book_size: code book size (a power of2, e.g. 16, 32256, 1024)
    # Outputs:
    # m: the code book as the centroids of the clusters
    # p: weight of each cluster, the number of its vectors divided by total
    # number of vectors 
    # dist_hist: total distortion history, a vector containing the overall
    # distortion of each iteration 
    # Method: 
    # The mean vector is split to two. the model is trained on those two vectors 
    # until the distortion does not vary much, then those are split to two and 
    # so on, until the desired number of clusters is reached.

    # Algorithm: 
    # 1. Find the mean 
    # 2. split each centroid to two
    # 3. Assign each data point to a centroid 
    # 4. Find the centroids 
    # 5. Calculate the total distance 
    # 6. If the distance has not changed much,
    # if the number of centroids is smaller than L2, go to step 2
    # else go to step 7
    # else (the distance has changed substantially) go to step 3
    # 7. Ift he number of centroids is larger than L, 
    # discard the Centroid with (highest distortion OR lowest population) 
    # go to step 3
    # 8. Calculate the Variances and Cluster Weights if required 
    # 9. End
    """

    #X to [X-e*X and X+e*X], Percentage for Splitting
    e = 0.01
    # Rate of reduction os split size after each splitting. i.e. e=e*e_red
    e_red = 0.75
    # threshold in improvement in Distortion
    dt = 0.005
    # before terminating and splitting again.
    # Rate of reduction of improvement Threshold, dt,
    dt_red = 0.75
    # after each splitting
    # population of each cluster should be at least 10#
    min_pop = 0.10
    # ofi ts quota (NILC)
    # Otherwise that codeword is replaced with another codeword 
    # Dimension, Number of Data points
    d, n = x.shape[0], x.shape[1]
    # First Iteration after Splitting
    is_first_round = True
    # Mean Vector
    m = [sum(x[i, :])/n for i in range(d)]
    # split to two vectors
    cb = [list(map(lambda val: (1+e)*val, m)), list(map(lambda val: (1-e)*val, m))]
    # Current size of the code book
    lc = len(cb)
    iterate, split = 0, 0
    is_there_a_best_cb = 0
    # The maximum number oft raining iterations at each
    max_iter_in_each_size = 20
    # code book size (The code book size starts from one and increases thereafter),
    each_size_iter_counter = 0
    dist_hist = []
    while True:
        # Distance Calculation 
        # Find the closest codeword to each data vector
        min_index, dst = vq_index(x, cb)
        cluster_d, population, low_pop = numpy.zeros((1, lc)), numpy.zeros((1, lc)), []
        # Find the Centroids (Mean of each Cluster)
        for i in range(lc):
            ind = []
            for j in range(len(min_index)):
                if i == min_index[j]:
                    ind.append(j)
            # if a cluster has very low population, remember it.
            if len(ind) < min_pop * n / lc:
                low_pop.append(i)
            else:
                cb[:, i] = mean(x[:, ind], 2)
                population[i] = len(ind)
                cluster_d[i] = sum(dst[ind])
        if not low_pop is None:
            temp, MaxInd = max_n(population, len(low_pop))
            # Replace low-population codewords with
            cb[:, low_pop] = cb[:, MaxInd] * (1 + e)
            # splits of high population codewords
            cb[:, MaxInd] = cb[:, MaxInd] * (1 - e)
            # re-train 
            min_index, dst = vq_index(x, cb)
            cluster_d = [0] * lc
            population = [0] * lc
            for i in range(lc):
                ind = filter(lambda x: x == i, min_index.index(i))
                if not ind is None:
                    cb[:, i] = mean(x[:, ind], 2)
                    population[i] = len(ind)
                    cluster_d[i] = sum(dst[ind])
                # if no vector is close enough to this codeword, replace it with a random vector
                else:
                    cb[:, i] = x[:, math.floor(rand() * n) + 1]
                    print('A random vector was assigned as a codeword.')
                    # At least another iteration is required
                    is_first_round = 1
        iterate += 1
        # First iteration after a split (do  not exit)

        PrevTotalDist = 0
        if is_first_round:
            TotalDist = sum(cluster_d)
            dist_hist.append(TotalDist)
            PrevTotalDist = TotalDist
            is_first_round = 0
        else:
            TotalDist = sum(cluster_d)
            dist_hist.append(TotalDist)
            PercentageImprovement = ((PrevTotalDist - TotalDist) / PrevTotalDist)
            # Improvement substantial
            if PercentageImprovement >= dt:
                # Save Distortion o/this iteration and continue training
                PrevTotalDist = TotalDist
                is_first_round = 0
            # Improvement NOT substantial (Saturation)
            else:
                each_size_iter_counter = 0
                # Enough Codewords ?
                if lc >= code_book_size:
                    # Exact number of codewords
                    if code_book_size == lc:
                        # disp(TotalDist)
                        break
                        # Kill one codeword at a time
                    else:
                        # Eliminate low population codewords
                        temp = min(population)
                        ind = population.index(temp)
                        NCB = cb[:, setxor1d(rand(lc), ind)]
                        cb = NCB
                        lc -= 1
                        is_first_round = 1
                # If not enough codewords exist yet, split more
                else:
                    cb = [cb * (1 + e), cb * (1 - e)]
                    # split size reduction
                    e *= e_red
                    # Improvement Threshold Reduction
                    dt *= dt_red
                    lc = size(cb, 2)
                    is_first_round = 1
                    split += 1
                    # As we just split this codebook, there is  no best
                    is_there_a_best_cb = 0
                    # codebook at this size yet.
        BestD = 0
        if not is_there_a_best_cb:
            BestCB = cb
            BestD = TotalDist
            is_there_a_best_cb = 1
        else:
            if TotalDist < BestD:
                BestCB = cb
                BestD = TotalDist
        each_size_iter_counter += 1
        # Ift oo many iterations in this size,
        if each_size_iter_counter > max_iter_in_each_size:
            # stop training this size
            each_size_iter_counter = 0
            # choose the best codebook so far
            cb = BestCB
            is_there_a_best_cb = 0
            # Enough Codewords ?
            if lc >= code_book_size:
                # Exact number of codewords
                if code_book_size == lc:
                    # disp(TotalDist)
                    break
                    # Kill one codeword at a time
                else:
                    temp = min(population)
                    ind = population.index(temp)
                    NCB = cb[:, setxor1d(range(lc), ind)]
                    cb = NCB
                    lc -= 1
                    is_first_round = 1
            # split
            else:
                cb = [cb * (1 + e), cb * (1 - e)]
                # split size reduction
                e *= e_red
                # Improvement Threshold Reduction
                dt *= dt_red
                lc = size(cb, 2)
                is_first_round = 1
                split += 1
                is_there_a_best_cb = 0
                # disp(lc)
        # disp(TotalDist)
        p = list(map(lambda y: y / n, population))
        #save CBTemp cb p dist_hist
    return cb, list(map(lambda y: y / n, population)), dist_hist


def main():
    # This is the main program, a script file. 
    digits = ['1', '2']
    # Input training wave files from 33 subjects whose initials are listed below
    man_subjects = ['AE']
    frame_rate = 100
    x, y = 0, 13
    train_cep_set = []
    for a in digits:
        for subject in man_subjects:
            train_cep_set.append(
                get_ceps(path_to_hmm_words + 'MAN/' + subject + '/' + a + 'A_endpt.wav', frame_rate, x, y))

    # Group cepstrum coefficients by digit(NixI3, i = 1. . 10) matricies
    tr_vectors = []
    #for each subject
    for i in train_cep_set:
        # cell of 10 digits
        for m in i:
            tr_vectors.append(list(m))
    # Get code book
    cbk, p, dh = vq_split(numpy.transpose(tr_vectors))
    cbk = numpy.transpose(cbk)

    n_digit, n_subject = len(digits), len(man_subjects)
    # Encode train ceps 
    '''trainseq = arrayfun(@(a) encode(a{1}, cbk, 0), train_cep_set, 'UniformOutput', false)
    # Re-index the traing sequence so that it goes by digit first 
    trseq = cell(1,n_digit)
    for i = 1:n_digit
      for m = 1:n_subject
        trseq{i}{m} = trainseq{m}{i}
      end 
    end 
    # Initialize HMM 
    trans = [0.34 0.33 0.33 0.00 0.000.00 0.34 0.33 0.33 0.000.00 0.00 0.34 0.33 0.330.00 0.00 0.00 0.50 0.500.00 0.00 0.00 0.00 1.0]
    # transitional probabilities 
    emis = ones(size(trans,1),32)./32
    # HMM training 
    [estTR, estE] = arrayfun(@(a) hmmtrain(a{1}, trans, emis), trseq, 'UniformOutput', false)
    # Testing begins: compute test ceps{or one su~ject JT, not in training set 
    testceps = arrayfun(@(a) getceps(strcat('isolated_digits_ti_train_endpt/MAN/JT/', ...
        a{1}, 'B_endpt.wav'), 1, frame_rate, x, y), digits, 'UniformOutput', false)
    # Encode test ceps with single subject flag set 
    testseq = arrayfun(@(a) encode(a{1}, cbk, 1), testceps, 'UniformOutput', false)
    # Compute the log-likelihood{or each test sequence 
    lp = []
    for i = 1:n_digit # go through all hmm model
      for j = 1:n_digit # go through all digits
        lp(i,j) = drecm(testseq{j}, estTR{i},estE{i})
      end 
    end 
    [mx, It] = max(lp)
    # Output recognized digits 
    #It;'''


main()
# encode([2,4,5,6,3,7,1,23,54,23,1,8,65,23,98,0,6], [45,7,2,87,34,76,34,7,2,0,8,1,3,4,5,7,9,4,6], True)