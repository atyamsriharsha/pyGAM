"""
generate some plots for the pyGAM repo
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

from pygam import *
from pygam.utils import generate_X_grid

np.random.seed(420)
fontP = FontProperties()
fontP.set_size('small')

# poisson, histogram smoothing
# custom GAM tree dataset
# new basis function thing
# wage dataset to illustrate partial dependence
# monotonic increasing, concave constraint on hep data
# prediction intervals on motorcycle data


def hepatitis():
    hep = pd.read_csv('datasets/hepatitis_A_bulgaria.csv').astype(float)
    # eliminate 0/0
    mask = (hep.total > 0).values
    hep = hep[mask]
    X = hep.age.values
    y = hep.hepatitis_A_positive.values / hep.total.values
    return X, y

def mcycle():
    motor = pd.read_csv('datasets/mcycle.csv', index_col=0)
    X = motor.times.values[:,None]
    y = motor.accel
    return X, y

def faithful():
    faithful = pd.read_csv('datasets/faithful.csv', index_col=0)
    y, xx, _ = plt.hist(faithful.values[:,0], bins=200, color='k')
    X = xx[:-1] + np.diff(xx)/2 # get midpoints of bins
    return X, y

def wage():
    wage = pd.read_csv('datasets/wage.csv', index_col=0)
    X = wage[['year', 'age', 'education']].values
    y = wage['wage'].values

    # change education level to integers
    X[:,-1] = np.unique(X[:,-1], return_inverse=True)[1]
    return X, y

def trees():
    trees = pd.read_csv('datasets/trees.csv', index_col=0)
    y = trees.Volume
    X = trees[['Girth', 'Height']]
    return X, y

def default():
    default = pd.read_csv('datasets/default.csv', index_col=0)
    default = default.values
    default[:,0] = np.unique(default[:,0], return_inverse=True)[1]
    default[:,1] = np.unique(default[:,1], return_inverse=True)[1]
    X = default[:,1:]
    y = default[:,0]
    return X, y

def cake():
    cake = pd.read_csv('datasets/cake.csv', index_col=0)
    X = cake[['recipe', 'replicate', 'temperature']].values
    X[:,0] = np.unique(cake.values[:,1], return_inverse=True)[1]
    X[:,1] -= 1
    y = cake['angle'].values
    return X, y

def gen_basis_fns():
    X, y = hepatitis()
    gam = LinearGAM(lam=.6, fit_intercept=False).fit(X, y)
    XX = generate_X_grid(gam)

    plt.figure()
    fig, ax = plt.subplots(2,1)
    ax[0].plot(XX, gam._modelmat(XX, feature=0).A);
    ax[0].set_title('b-Spline Basis Functions')

    ax[1].scatter(X, y, facecolor='gray', edgecolors='none')
    ax[1].plot(XX, gam._modelmat(XX).A * gam.coef_);
    ax[1].plot(XX, gam.predict(XX), 'k')
    ax[1].set_title('Fitted Model')
    fig.tight_layout()
    plt.savefig('imgs/pygam_basis.png', dpi=300)

def cake_data_in_one():
    X, y = cake()

    gam = LinearGAM(fit_intercept=True)
    gam.gridsearch(X,y)

    XX = generate_X_grid(gam)

    plt.figure()
    plt.plot(gam.partial_dependence(XX))
    plt.title('LinearGAM')
    plt.savefig('imgs/pygam_cake_data.png', dpi=300)

def faithful_data_poisson():
    X, y = faithful()
    gam = PoissonGAM().gridsearch(X, y)

    plt.figure()
    plt.bar(X, y, width=np.diff(X)[0], color='k')

    plt.plot(X, gam.predict(X), color='r')
    plt.title('Best Lamba: {0:.2f}'.format(gam.lam))
    plt.savefig('imgs/pygam_poisson.png', dpi=300)

def single_data_linear():
    X, y = mcycle()

    gam = LinearGAM()
    gam.gridsearch(X, y)

    # single pred linear
    plt.figure()
    plt.scatter(X, y, facecolor='gray', edgecolors='none')
    plt.plot(X, gam.predict(X), color='r')
    plt.title('Best Lamba: {0:.2f}'.format(gam.lam))
    plt.savefig('imgs/pygam_single_pred_linear.png', dpi=300)

def mcycle_data_linear():
    X, y = mcycle()

    gam = LinearGAM()
    gam.gridsearch(X, y)

    XX = generate_X_grid(gam)
    plt.figure()
    plt.scatter(X, y, facecolor='gray', edgecolors='none')
    plt.plot(XX, gam.predict(XX), 'r--')
    plt.plot(XX, gam.prediction_intervals(XX, width=.95), color='b', ls='--')
    plt.title('95% prediction interval')

    plt.savefig('imgs/pygam_mcycle_data_linear.png', dpi=300)

def wage_data_linear():
    X, y = wage()

    gam = LinearGAM(n_splines=10)
    gam.gridsearch(X, y, lam=np.logspace(-5,3,50))

    XX = generate_X_grid(gam)

    plt.figure()
    fig, axs = plt.subplots(1,3)

    titles = ['year', 'age', 'education']
    for i, ax in enumerate(axs):
        ax.plot(XX[:, i], gam.partial_dependence(XX, feature=i+1))
        ax.plot(XX[:, i], *gam.partial_dependence(XX, feature=i+1, width=.95)[1],
                c='r', ls='--')
        if i == 0:
            ax.set_ylim(-30,30);
        ax.set_title(titles[i])

    fig.tight_layout()
    plt.savefig('imgs/pygam_wage_data_linear.png', dpi=300)

def default_data_logistic(n=500):
    X, y = default()

    gam = LogisticGAM()
    gam.gridsearch(X, y)

    XX = generate_X_grid(gam)

    plt.figure()
    fig, axs = plt.subplots(1,3)

    titles = ['student', 'balance', 'income']
    for i, ax in enumerate(axs):
        ax.plot(XX[:, i], gam.partial_dependence(XX, feature=i+1))
        ax.plot(XX[:, i], *gam.partial_dependence(XX, feature=i+1, width=.95)[1],
                c='r', ls='--')
        ax.set_title(titles[i])

    fig.tight_layout()
    plt.savefig('imgs/pygam_default_data_logistic.png', dpi=300)

def constraints():
    X, y = hepatitis()

    plt.figure()
    fig, ax = plt.subplots(1,2)

    gam = LinearGAM(constraints='monotonic_inc').fit(X, y)
    ax[0].plot(X, y, label='data')
    ax[0].plot(X, gam.predict(X), label='monotonic fit')
    ax[0].legend()

    gam = LinearGAM(constraints='concave').fit(X, y)
    ax[1].plot(X, y, label='data')
    ax[1].plot(X, gam.predict(X), label='concave fit')
    ax[1].legend()

    fig.tight_layout()
    plt.savefig('imgs/pygam_constraints.png', dpi=300)

    plt.figure()
    gam = LinearGAM(constraints='monotonic_dec').fit(X, y)
    plt.plot(X, y, label='data')
    plt.plot(X, gam.predict(X))
    plt.title('very un-useful monotonic decreasing fit')

    plt.savefig('imgs/pygam_constraints_dec.png', dpi=300)

def trees_data_custom():
    X, y = trees()
    gam = GAM(distribution='gamma', link='log', n_splines=4)
    gam.gridsearch(X, y)

    plt.figure()
    plt.scatter(y, gam.predict(X))
    plt.xlabel('true volume')
    plt.ylabel('predicted volume')
    plt.savefig('imgs/pygam_custom.png', dpi=300)

# def gen_single_data(n=200):
#     """
#     1-dimensional Logistic problem
#     """
#     x = np.linspace(-5,5,n)[:,None]
#
#     log_odds = -.5*x**2 + 5
#     p = 1/(1+np.exp(-log_odds)).squeeze()
#     y = (np.random.rand(len(x)) < p).astype(np.int)
#
#     lgam = LogisticGAM()
#     lgam.fit(x, y)
#
#     # title plot
#     plt.figure()
#     plt.plot(x, p, label='true probability', color='b', ls='--')
#     plt.scatter(x, y, label='observations', facecolor='None')
#     plt.plot(x, lgam.predict_proba(x), label='GAM probability', color='r')
#     plt.legend(prop=fontP, bbox_to_anchor=(1.1, 1.05))
#     plt.title('LogisticGAM on quadratic log-odds data')
#     plt.savefig('imgs/pygam_single.png', dpi=300)
#
#     # single pred
#     plt.figure()
#     plt.scatter(x, y, facecolor='None')
#     plt.plot(x, lgam.predict_proba(x), color='r')
#     plt.title('Accuracy: {}'.format(lgam.accuracy(X=x, y=y)))
#     plt.savefig('imgs/pygam_single_pred.png', dpi=300)
#
#     # UBRE Gridsearch
#     scores = []
#     lams = np.logspace(-4,2, 51)
#     for lam in lams:
#         lgam = LogisticGAM(lam=lam)
#         lgam.fit(x, y)
#         scores.append(lgam.statistics_['UBRE'])
#     best = np.argmin(scores)
#
#     plt.figure()
#     plt.plot(lams, scores)
#     plt.scatter(lams[best], scores[best], facecolor='None')
#     plt.xlabel('$\lambda$')
#     plt.ylabel('UBRE')
#     plt.title('Best $\lambda$: %.3f'% lams[best])
#
#     plt.savefig('imgs/pygam_lambda_gridsearch.png', dpi=300)


def gen_multi_data(n=200):
    """
    multivariate Logistic problem
    """
    n = 5000
    x = np.random.rand(n,5) * 10 - 5
    cat = np.random.randint(0,4, n)
    x = np.c_[x, cat]
    log_odds = (-0.5*x[:,0]**2) + 5 +(-0.5*x[:,1]**2) + np.mod(x[:,-1], 2)*-30
    p = 1/(1+np.exp(-log_odds)).squeeze()

    obs = (np.random.rand(len(x)) < p).astype(np.int)

    lgam = LogisticGAM()
    lgam.fit(x, obs)

    plt.figure()
    plt.plot(lgam.partial_dependence(np.sort(x, axis=0)))
    plt.savefig('imgs/pygam_multi_pdep.png', dpi=300)

if __name__ == '__main__':
    gen_basis_fns()
    faithful_data_poisson()
    wage_data_linear()
    default_data_logistic()
    constraints()
    trees_data_custom()
    mcycle_data_linear()
    cake_data_in_one()
    gen_multi_data()
