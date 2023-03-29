import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVC
import sklearn.model_selection as model_selection
from sklearn.metrics import accuracy_score, ConfusionMatrixDisplay, balanced_accuracy_score, confusion_matrix
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import learning_curve, train_test_split, ShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


def calculate_features(array):
    # compute the eigenvalues of an object file
    points_centered = array - np.mean(array, axis=0)
    pca = PCA(n_components=3)
    pca.fit(points_centered)
    eigenvalues = pca.explained_variance_
    planarity = (eigenvalues[1] - eigenvalues[2]) / eigenvalues[0]
    sphericity = eigenvalues[2] / eigenvalues[0]

    # compute the highest z-value of an object file
    highest_z = np.max(array[:, 2])

    # compute the width, length, height of the bbox of an object file
    relative_height = np.max(array[:, 2]) - np.min(array[:, 2])
    width_temp = np.max(array[:, 0]) - np.min(array[:, 0])
    length_temp = np.max(array[:, 1]) - np.min(array[:, 1])
    width = min(width_temp, length_temp)
    length = max(width_temp, length_temp)
    bbox_vol = width * relative_height * length

    # compute the deviation of the all the points of an object file
    std_xyz = np.std(array, axis=0)  # the x, y and z-axis standard deviation
    x_std = std_xyz[0]
    y_std = std_xyz[1]
    z_std = std_xyz[2]

    # compute the overall std
    x_array = array[:, 0]
    y_array = array[:, 1]
    z_array = array[:, 2]
    x_ = (x_array - np.mean(x_array)) ** 2
    y_ = (y_array - np.mean(y_array)) ** 2
    z_ = (z_array - np.mean(z_array)) ** 2
    n = array.shape[0]
    point_std = np.sum(np.concatenate((x_, y_, z_))) / n

    # return np.array([heighest, relative_height, length, width, bbox_vol, eigenvalues[0], eigenvalues[1]])
    # return np.array([relative_height, length, width, bbox_vol, eigenvalues[0], planarity, sphericity])
    return np.array([highest_z, point_std, relative_height, length, width, bbox_vol, eigenvalues[0], planarity, sphericity])


def calculate_matric(ylabel, ypred):
    OA = accuracy_score(ylabel, ypred)
    mA = balanced_accuracy_score(ylabel, ypred)
    class_names = [0, 1, 2, 3, 4]
    disp_names = ['building', 'car', 'fence', 'pole', 'tree']
    conf = confusion_matrix(ylabel, ypred, labels=class_names)
    disp = ConfusionMatrixDisplay(confusion_matrix=conf, display_labels = disp_names)
    disp.plot()
    plt.show()
    return OA, mA, conf


def feature_visualisation(array):
    fig = plt.figure()
    fig.suptitle('Feature subset visualisation of 5 classes')
    colors = ['firebrick', 'grey', 'darkorange', 'dodgerblue', 'olivedrab']
    labels = ['building', 'car', 'fence', 'pole', 'tree']

    ax = fig.add_subplot(131, projection='3d')
    ax.title.set_text('highest_z & point_std & bbox_vol')
    for i in range(5):
        ax.scatter(array[100*i:100*(i+1), 0], array[100*i:100*(i+1), 1], array[100*i:100*(i+1), 5],
                   marker='o', c=colors[i], alpha=0.8, label=labels[i])
    ax.set_xlabel('x1:highest z-value')
    ax.set_ylabel('x2:point standard deviation')
    ax.set_zlabel('x3:bounding box volume')

    ax = fig.add_subplot(132, projection='3d')
    ax.title.set_text('relative_height & length & width')
    for i in range(5):
        ax.scatter(array[100*i:100*(i+1), 2], array[100*i:100*(i+1), 3], array[100*i:100*(i+1), 4],
                   marker='o', c=colors[i], alpha=0.8, label=labels[i])
    ax.set_xlabel('x1:relative_height')
    ax.set_ylabel('x2:length')
    ax.set_zlabel('x3:width')

    ax = fig.add_subplot(133, projection='3d')
    ax.title.set_text('lambda 1 & planarity & sphericity')
    for i in range(5):
        ax.scatter(array[100*i:100*(i+1), 6], array[100*i:100*(i+1), 7], array[100*i:100*(i+1), 8],
                   marker='o', c=colors[i], alpha=0.8, label=labels[i])
    ax.set_xlabel('x1:eigenvalue_lambda1')
    ax.set_ylabel('x2:planarity')
    ax.set_zlabel('x3:sphericity')

    ax.legend()
    plt.show()


def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None, n_jobs=1,
                        train_sizes=np.linspace(.1, 1.0, 5)):
    plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel('Training example')
    plt.ylabel('Overall accuracy score')
    train_sizes, train_scores, test_scores = learning_curve(estimator, X, y,
                                                           cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()
    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt



def main():
    # loop over the 500 files to generate input datasets
    l1 = []
    for i in range(500):
        file_name = '../data/{:03d}.xyz'.format(i)
        # print(file_name)
        data = np.genfromtxt(file_name, usecols=[0, 1, 2])
        features = calculate_features(data)
        l1.append(features)

    data_list = np.array(l1)

    # read data and calculate features

    # create ground truth label set
    b = np.repeat(0, 100)  # 1-building
    c = np.repeat(1, 100)  # 2-car
    f = np.repeat(2, 100)  # 3-fence
    p = np.repeat(3, 100)  # 4-pole
    t = np.repeat(4, 100)  # 5-tree
    label = np.concatenate((b, c, f, p, t))

    # breakpoint()
    # SVM classification
    X_train, X_test, y_train, y_test = model_selection.train_test_split(data_list, label,
                                                                        train_size=0.60, test_size=0.4,
                                                                        random_state=101)

    # the optimal kernel function for SVM, RF classifier
    svm = SVC(kernel='linear', C=100).fit(X_train, y_train)
    rf = RandomForestClassifier(max_depth=20, min_samples_leaf=2, min_samples_split=10, n_estimators=50,
                                random_state=42).fit(X_train, y_train)

    svm_pred = svm.predict(X_test)
    rf_pred = rf.predict(X_test)
    OA_svm, mA_svm, conf_svm = calculate_matric(y_test, svm_pred)
    OA_rf, mA_rf, conf_rf = calculate_matric(y_test, rf_pred)

    # train_test learning curve
    cv = ShuffleSplit(n_splits=10, test_size=0.2, random_state=0)
    plot_learning_curve(svm, 'Learning Curves (SVM, linear kernel, $C=100$)',
                        data_list, label, cv=cv, n_jobs=16)
    plot_learning_curve(rf, "Learning Curves RF($max_depth=20$, $min_samples_leaf=2$, $min_samples_split=10$, $n_estimators=50$, "
                            "$random_state=42$)", data_list, label, cv=cv, n_jobs=16)

    # show the subset features plot
    feature_visualisation(data_list)

    print("For SVM, Overall Accuracy: {0}, Mean Accuracy: {1}".format(OA_svm, mA_svm))
    print("For RF, Overall Accuracy: {0}, Mean Accuracy: {1}".format(OA_rf, mA_rf))


if __name__ == '__main__':
    main()
