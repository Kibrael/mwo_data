
# coding: utf-8

# In[1]:


import cv2
import numpy as np


# In[2]:


#constants
CELL_SIZE = 20 #size of image (for cutting sheet?)
NCLASSES = 10 #number of digits 0-9
TRAIN_RATIO = 0.8  # Part of all samples used for training.


# In[29]:


digits_img = cv2.imread('data/digits.png', 0)
print(digits_img.shape)
digits_img


# In[25]:


#// is floor division (round down to nearest whole number)
#hsplit cuts into columns
#vsplit cuts into rows
digits = [np.hsplit(r, digits_img.shape[1] // CELL_SIZE) for r in np.vsplit(digits_img, digits_img.shape[0] // CELL_SIZE)]
digits


# In[28]:


len(digits[0])


# In[31]:


digits = np.array(digits).reshape(-1, CELL_SIZE, CELL_SIZE)
print(digits.shape)
digits


# In[33]:


nsamples = digits.shape[0]
print(nsamples)
labels = np.repeat(np.arange(NCLASSES), nsamples // NCLASSES)
len(labels)


# In[34]:


for i in range(nsamples):
        #Image Moment is a particular weighted average of image pixel intensities, used to find centroids in pics
    m = cv2.moments(digits[i]) #create dict of moments
    print(m)
    if m['mu02'] > 1e-3:
        s = m['mu11'] / m['mu02']
        M = np.float32([[1, -s, 0.5*CELL_SIZE*s], [0, 1, 0]])
        digits[i] = cv2.warpAffine(digits[i], M, (CELL_SIZE, CELL_SIZE))


# In[7]:


perm = np.random.permutation(nsamples)
digits = digits[perm]
labels = labels[perm]


# In[8]:


def calc_hog(digits):
        win_size = (20, 20)
        block_size = (10, 10)
        block_stride = (10, 10)
        cell_size = (10, 10)
        nbins = 9
        hog = cv2.HOGDescriptor(win_size, block_size, block_stride,
     cell_size, nbins)
        samples = []
        for d in digits: samples.append(hog.compute(d))
        return np.array(samples, np.float32)


# In[10]:


ntrain = int(TRAIN_RATIO * nsamples)
fea_hog_train = calc_hog(digits[:ntrain])
fea_hog_test = calc_hog(digits[ntrain:])
labels_train, labels_test = labels[:ntrain], labels[ntrain:]


# In[11]:


ntrain = int(TRAIN_RATIO * nsamples)
fea_hog_train = calc_hog(digits[:ntrain])
fea_hog_test = calc_hog(digits[ntrain:])
labels_train, labels_test = labels[:ntrain], labels[ntrain:]


# In[15]:


svm_model = cv2.ml.SVM_create()
svm_model.setGamma(2)
svm_model.setC(1)
svm_model.setKernel(cv2.ml.SVM_RBF)
svm_model.setType(cv2.ml.SVM_C_SVC)
svm_model.train(fea_hog_train, cv2.ml.ROW_SAMPLE, labels_train)


# In[16]:


def eval_model(fea, labels, fpred):
    pred = fpred(fea).astype(np.int32)
    acc = (pred.T == labels).mean()*100
    conf_mat = np.zeros((NCLASSES, NCLASSES), np.int32)
    for c_gt, c_pred in zip(labels, pred):
        conf_mat[c_gt, c_pred] += 1
    return acc, conf_mat


# In[17]:


svm_acc, svm_conf_mat = eval_model(fea_hog_test, labels_test,
lambda fea: svm_model.predict(fea)[1])
print('SVM accuracy (%):', svm_acc)
print('SVM confusion matrix:')
print(svm_conf_mat)


# In[21]:


dir(digits_img)


# In[22]:


digits_img.shape

