# importing libraries
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
import joblib

def preprocesses():
    """preprocesses the data:
    parameter:
    return :
    """
    df = pd.read_csv(r"D:\Arai4_Projects\kpmgProject\data\B\metadata_with_fr_nl_info.csv")
    #df = pd.read_csv('/data/B/metadata_with_fr_nl_info.csv')
    df = df[['text_nl','label']] # selecting feature and target for modeling
    df = df.astype(str)
    df = df.dropna()
    
    return df


    
###################################################################################################################  



def balance_sample_down(df):
    """downsample the data
     
    """
    
    # Separate majority and minority classes
    df_majority = df[df.label == "new"]
    df_minority = df[df.label == "modified"]
    
 
    #downsample majority class
    df_majority_downsampled = resample(df_majority, 
                                 replace=False,     # sample with replacement
                                 n_samples = 257,    # to match majority class
                                 random_state =123) # reproducible results
 
    # Combine majority class with upsampled minority class
    df_downsampled = pd.concat([df_majority_downsampled, df_minority])
 
    # Display new class counts
    print("Down sampled: ", df_downsampled.label.value_counts())

    y = df_downsampled.label
    X = df_downsampled['text_nl'].to_list()
    

    return X, y



    ##############################################################################################################


def classifier_model():
    """classifier 
    """
    df = preprocesses()
    X,y = balance_sample_down(df)
    X_train, X_test, Y_train, Y_test = train_test_split(X,y,test_size=1/5,random_state=42) 
    
    # conveting to desired array fromat
    y_train =Y_train.to_numpy()
    y_train =np.reshape(y_train, (-1, 1))
    y_test = Y_test.to_numpy()
    y_test = np.reshape(y_test,(-1, 1))
    

    mlb_1 = MultiLabelBinarizer()
    y_train = mlb_1.fit_transform(y_train)
    y_test = mlb_1.fit_transform(y_test)
  
    

    classifier = Pipeline([
         ('vectorizer', CountVectorizer()),
         ('tfidf', TfidfTransformer()),
         ('clf', MultiOutputClassifier(OneVsRestClassifier(LinearSVC())))])

    classifier.fit(X_train, y_train)
    predicted = classifier.predict(X_test)
    joblib.dump(classifier, 'label.pkl')
    all_labels = mlb_1.inverse_transform(predicted)



############################################################################################################


def label_text(deposit):

    df = pd.read_csv(r"D:\Arai4_Projects\kpmgProject\data\B\metadata_with_fr_nl_info_summary.csv")
    df = df.set_index('deposit_number')
    text_data = df['text_nl'][deposit]
    prediction =joblib.load('label.pkl').predict([text_data]).flat[0]

    if prediction == 0:
        label = 'modified'
    elif prediction == 1:
        label = 'new'
    else:
        label = '--'

        
    return label
    

