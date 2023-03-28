import numpy as np
from sklearn import svm
import sklearn.model_selection as model_selection
from refit_strategy import refit_strategy
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import PCA


def calculate_features(array):
    points_centered = array - np.mean(array, axis=0)
    pca = PCA(n_components=3)
    pca.fit(points_centered)
    eigenvalues = pca.explained_variance_

    relative_height = np.max(array[:, 2]) - np.min(array[:, 2])

    width_temp = np.max(array[:, 0]) - np.min(array[:, 0])
    length_temp = np.max(array[:, 1]) - np.min(array[:, 1])
    width = min(width_temp, length_temp)
    length = max(width_temp, length_temp)

    bbox_vol = width * relative_height * length

    return np.array([relative_height, length, width, bbox_vol, eigenvalues[0], eigenvalues[1]])


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
    b = np.repeat(1, 100)  # 1-building
    c = np.repeat(2, 100)  # 2-car
    f = np.repeat(3, 100)  # 3-fence
    p = np.repeat(4, 100)  # 4-pole
    t = np.repeat(5, 100)  # 5-tree
    label = np.concatenate((b, c, f, p, t))

    # breakpoint()
    # SVM classification
    X_train, X_test, y_train, y_test = model_selection.train_test_split(data_list, label,
                                                                        train_size=0.60, test_size=0.4,
                                                                        random_state=101)
    # breakpoint()
    scores = ["accuracy", "balanced_accuracy"]

    tuned_parameters = [
        {"kernel": ["rbf"], "gamma": [1e-3, 1e-4], "C": [1, 10, 100, 1000]},
        {"kernel": ["poy"], "degree": [1, 2, 3, 4, 5], "C": [1, 10, 100, 1000]},
        {"kernel": ["linear"], "C": [1, 10, 100, 1000]},
    ]

    print("starting grid search")
    grid_search = GridSearchCV(
        svm.SVC(), tuned_parameters, scoring=scores, refit=refit_strategy
    )
    grid_search.fit(X_train, y_train)
    grid_search.best_params_


if __name__ == '__main__':
    main()
