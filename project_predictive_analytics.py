# -*- coding: utf-8 -*-
"""Project Predictive Analytics.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Deyr_bqWWLPAlSMszpw5xDfSpzv80Hb-

# Bank Marketing Term Deposit Forecasting

---

Dataset dapat di unduh melalui [tautan ini](https://www.kaggle.com/datasets/janiobachmann/bank-marketing-dataset/code)

# Import Necessary Library

---
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
# %matplotlib inline
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import OneHotEncoder

from sklearn.model_selection import train_test_split

from sklearn.preprocessing import StandardScaler

from sklearn import linear_model
from sklearn.metrics import classification_report
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV

"""# Data Loading

---


"""

df = pd.read_csv('bank.csv')
df

"""# EDA (Exploratory Data Analysis)

---



> ## Deskripsi Variabel

Info data: diketahui memiliki 17 column dan 11162 baris dengan tipe data int, object.


"""

df.info()

"""melihat diskripsi data seperti nilai *min max*, mean, standart deviasi dll."""

df.describe()

"""

> ## Missing Value and Duplicate

"""

df.isnull().sum()

df.duplicated().sum()

"""

> ## Univariate dan Multivariate Analysis

### Categorical Features

Mengambil data dengan tipe data object.
"""

cat_data = df.select_dtypes(exclude='number').columns.drop(['deposit', 'job'])
cat_data

"""Membuat plot data kategori yang dibagi berdasarkan nilai deposit."""

plt.figure(figsize=(13,15))
for i,cat_fea in enumerate(cat_data):
    plt.subplot(5,2,i+1)
    sns.countplot(x=cat_fea, hue='deposit', data=df,edgecolor="black")
    plt.title("Countplot of {}  by deposit".format(cat_fea))
plt.tight_layout()    
plt.show()
plt.figure(figsize=[15,5])
sns.countplot(x='job', hue='deposit',edgecolor="black",data=df)
plt.title("Countplot of job by deposit")
plt.show()

"""didapat hasil data yang imbalance pada *default* terlihat dari jarak jumlah dua kategori data

### Numerical Features

Mengambil data dengan tipe data numerik.
"""

num_data = df.select_dtypes(include='number')
num_data.head()

"""Membuat plot data numerik menggunakan scatter plot untuk mengetahui apakah ada outlier pada data."""

plt.figure(figsize=(13,15))
for i,num_fea in enumerate(num_data):
    plt.subplot(4,2,i+1)
    stats.probplot(df[num_fea], dist='norm', plot=plt)
    plt.title("Probability Plot {}".format(num_fea))
plt.tight_layout()    
plt.show()

"""Membuat plot data numerik yang dibagi berdasarkan nilai deposit."""

plt.figure(figsize=(13,15))
for i,v in enumerate(num_data):
    print(i,v)
    plt.subplot(4,2,i+1)
    sns.scatterplot(x=v,y=df['deposit'], data=num_data, color='blue')
    plt.title("scatterplot of {}  by deposit".format(v),size=15)
    plt.xlabel("{}".format(v),size=15)
    plt.ylabel("Deposit",size=15)
plt.tight_layout()
plt.show()

"""Membuat matriks korelasi data numerik."""

plt.figure(figsize=(10,8),dpi=80)
sns.heatmap(num_data.corr(),cmap="coolwarm",annot=True,linewidth=0.5)
plt.yticks(rotation=55)

"""didapat hasil data yang balance dan pada korelasi data *pdays* dan *previous* yang positive maka bisa menggunakan salah satunya saja

### Outliers dan Down-Sampling
"""

df.drop(columns =['default' ,'pdays'] ,axis =1 ,inplace = True)

"""## Target Data

mengecek apakah data target sudah balance.
"""

df['deposit'].value_counts()

plt.figure(figsize=(15,5))
plt.subplot(1,2,2)
labels =df['deposit'].value_counts(sort = True).index
sizes = df['deposit'].value_counts(sort = True)
plt.pie(sizes,labels=labels,autopct='%1.1f%%', startangle=270,)
plt.title('Total yes and No category',size = 15)
plt.show()

"""data target sudah balance dengan dua kategori

# Data Preparation


---



> ## Encoding Data 

### Boolean type

melakukan one-hot encoding pada data boolean yaitu angka 1 untuk kategori 'yes' dan angka 0 untuk kategori 'no'
"""

df.select_dtypes('object').columns

boolean_cols = ['deposit', 'housing', 'loan']
for i in boolean_cols:
  df[i+'_new'] = df[i].apply(lambda x :1 if x =='yes' else 0)
  df.drop(i, axis=1, inplace=True)
df.head()

"""
### Category type


melakukan one-hot encoding untuk data kategori dimana akan bernilai 1 untuk setiap kategori yang bernilai benar"""

cat_cols = ['job', 'marital', 'education', 'contact', 'month', 'poutcome']
for i in cat_cols:
  df = pd.concat([df, pd.get_dummies(df[i], prefix=i)],axis=1)
  df.drop([i], axis=1, inplace=True)
df.head()

"""melihat hasil akhir atau final data"""

df

df.deposit_new

"""

> ## Split Dataset

split data dengan proporsi 8:2 dengan 8 untuk data train dan 2 untuk data test nya"""

X = df.drop(['deposit_new'], axis=1)
y = df['deposit_new']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 100)

print(len(X_train))
print(len(X_test))

"""cek lagi diskripsi data apakah memiliki skala yang berjauhan setelah dilakukan cleaning data dan preprocessing"""

X_train.describe()

"""didapat hasil standar deviasi yang skalanya berjauhan dengan data yang dilakukan one-hot encoding"""

df.columns

"""> ## Standarisasi

Untuk menyamakan standar deviasi antara data yang dilakukan one-hot endcoding (data kategori) dengan data numerik agar tidak terjadi bias. Proses ini dilakukan setelah split data untuk menghindari kebocoran target.
"""

num_data = ['age', 'balance', 'day', 'duration', 'campaign', 'previous']
scaler = StandardScaler()
scaler.fit(X_train[num_data])
X_train[num_data] = scaler.transform(X_train.loc[:, num_data])
X_test[num_data] = scaler.transform(X_test.loc[:, num_data])
X_train[num_data].describe().round(2)

"""# Modeling


---



> ## Model Training

Menggunakan logistic regression
"""

model = linear_model.LogisticRegression(solver='liblinear')
model.fit(X_train, y_train)

"""> ## Model Evaluation


Mendefinisikan hyperparameter tuning untuk model
"""

penalty = ['l1', 'l2']
C = np.logspace(2,5,20)

"""memasukkan hyperparameters kedalam dictionary untuk digunakan pada  model"""

hyperparameters = dict(penalty=penalty, C=C)

"""Mengatur hyperparameter tuning menggunakan Grid search"""

clf = GridSearchCV(model, hyperparameters, cv=5, verbose=True, n_jobs=-1)

"""Fit model menggunakan best_model hasil dari Grid search"""

best_model = clf.fit(X_train, y_train)

"""print hasil hyperparameter best model"""

print('Best Penalty:', best_model.best_estimator_.get_params()['penalty'])
print('Best C:', best_model.best_estimator_.get_params()['C'])

y_pred = best_model.predict(X_test)

"""Evaluasi model menggunakan confusion matrix"""

print(classification_report(y_test, y_pred))
roc_auc_score(y_test, y_pred)