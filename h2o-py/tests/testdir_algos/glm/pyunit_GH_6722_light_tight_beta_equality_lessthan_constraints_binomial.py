import h2o
from h2o.estimators.glm import H2OGeneralizedLinearEstimator as glm
from tests import pyunit_utils
from tests.pyunit_utils import utils_for_glm_hglm_tests

def test_light_tight_linear_constraints_binomial():
    '''
    Test constrained GLM with beta, equality and less than and equal to constraints.  The constraints are not very 
    tight.  However, coefficients from GLM built without constraints won't be able to satisfied the constraints.
    Constrained GLM models are built with coefficients initialized with coefficients from GLM built without constraints,
    default coefficients and random coefficients. 
    '''
    train = h2o.import_file(path=pyunit_utils.locate("smalldata/glm_test/binomial_20_cols_10KRows.csv"))
    for ind in range(10):
        train[ind] = train[ind].asfactor()
    train["C21"] = train["C21"].asfactor()
    response = "C21"
    predictors = list(range(0,20))

    light_tight_constraints = [] # this constraint is satisfied by default coefficient initialization
    # add beta constraints
    bc = []
    name = "C11"
    lower_bound = -7
    upper_bound = 0
    bc.append([name, lower_bound, upper_bound])

    name = "C18"
    lower_bound = 7.5
    upper_bound = 8
    bc.append([name, lower_bound, upper_bound])

    name = "C15"
    lower_bound = -4.5
    upper_bound = 0
    bc.append([name, lower_bound, upper_bound])

    name = "C16"
    lower_bound = -9
    upper_bound = 0.3
    bc.append([name, lower_bound, upper_bound])

    beta_constraints = h2o.H2OFrame(bc)
    beta_constraints.set_names(["names", "lower_bounds", "upper_bounds"])
    
    h2o_glm = glm(family="binomial", lambda_=0.0, solver="irlsm", seed=12345, standardize=True)
    h2o_glm.train(x=predictors, y=response, training_frame=train)
    logloss = h2o_glm.model_performance()._metric_json['logloss']
    print("logloss with no constraints: {0}".format(logloss))

    # add light tight constraints
    name = "C19"
    values = 0.5
    types = "Equal"
    contraint_numbers = 0
    light_tight_constraints.append([name, values, types, contraint_numbers])

    name = "C10.1"
    values = -0.3
    types = "Equal"
    contraint_numbers = 0
    light_tight_constraints.append([name, values, types, contraint_numbers])

    name = "constant"
    values = -1.00
    types = "Equal"
    contraint_numbers = 0
    light_tight_constraints.append([name, values, types, contraint_numbers])

    name = "C18"
    values = 0.75
    types = "Equal"
    contraint_numbers = 1
    light_tight_constraints.append([name, values, types, contraint_numbers])

    name = "C20"
    values = -0.13
    types = "Equal"
    contraint_numbers = 1
    light_tight_constraints.append([name, values, types, contraint_numbers])

    name = "constant"
    values = -6.9
    types = "Equal"
    contraint_numbers = 1
    light_tight_constraints.append([name, values, types, contraint_numbers])

    # add loose constraints
    name = "C19"
    values = 0.5
    types = "LessThanEqual"
    contraint_numbers = 2
    light_tight_constraints.append([name, values, types, contraint_numbers])

    name = "C20"
    values = -0.8
    types = "LessThanEqual"
    contraint_numbers = 2
    light_tight_constraints.append([name, values, types, contraint_numbers])

    name = "constant"
    values = -6
    types = "LessThanEqual"
    contraint_numbers = 2
    light_tight_constraints.append([name, values, types, contraint_numbers])

    name = "C12"
    values = 2
    types = "LessThanEqual"
    contraint_numbers = 3
    light_tight_constraints.append([name, values, types, contraint_numbers])

    name = "C13"
    values = -3
    types = "LessThanEqual"
    contraint_numbers = 3
    light_tight_constraints.append([name, values, types, contraint_numbers])

    name = "constant"
    values = -21
    types = "LessThanEqual"
    contraint_numbers = 3
    light_tight_constraints.append([name, values, types, contraint_numbers])   

    linear_constraints2 = h2o.H2OFrame(light_tight_constraints)
    linear_constraints2.set_names(["names", "values", "types", "constraint_numbers"])

    # GLM model with GLM coefficients with default initialization
    constraint_eta0 = [0.1258925]
    constraint_tau = [1.2, 1.5]
    constraint_alpha = [0.1]
    constraint_beta = [0.9]
    constraint_c0 = [5, 10] # initial value
    # GLM model with with GLM coefficients set to GLM model coefficients built without constraints
    h2o_glm_optimal_init = utils_for_glm_hglm_tests.constraint_glm_gridsearch(train, predictors, response, solver="IRLSM",
                                                                         family="binomial",
                                                                         linear_constraints=linear_constraints2,
                                                                         beta_constraints=beta_constraints,
                                                                         init_optimal_glm=True,
                                                                         constraint_eta0=constraint_eta0,
                                                                         constraint_tau=constraint_tau,
                                                                         constraint_alpha=constraint_alpha,
                                                                         constraint_beta=constraint_beta,
                                                                         constraint_c0=constraint_c0,
                                                                         return_best=False, epsilon=0.5)
    optimal_init_logloss = h2o_glm_optimal_init.model_performance()._metric_json['logloss']
    print("logloss with optimal GLM coefficient initializaiton: {0}, number of iterations taken to build the model: "
          "{1}".format(optimal_init_logloss, utils_for_glm_hglm_tests.find_model_iterations(h2o_glm_optimal_init)))
    print(glm.getConstraintsInfo(h2o_glm_optimal_init))
    
    h2o_glm_default_init = utils_for_glm_hglm_tests.constraint_glm_gridsearch(train, predictors, response, solver="IRLSM",
                                                                         family="binomial",
                                                                         linear_constraints=linear_constraints2,
                                                                         beta_constraints=beta_constraints,
                                                                         init_optimal_glm=False,
                                                                         constraint_eta0=constraint_eta0,
                                                                         constraint_tau=constraint_tau,
                                                                         constraint_alpha=constraint_alpha,
                                                                         constraint_beta=constraint_beta,
                                                                         constraint_c0=constraint_c0,
                                                                         return_best=False, epsilon=0.5)
    default_init_logloss = h2o_glm_default_init.model_performance()._metric_json['logloss']
    print("logloss with default GLM coefficient initializaiton: {0}, number of iterations taken to build the model: "
          "{1}".format(default_init_logloss, utils_for_glm_hglm_tests.find_model_iterations(h2o_glm_default_init)))
    print(glm.getConstraintsInfo(h2o_glm_default_init))
    random_coef = [0.9740393731418461, 0.9021970400494406, 0.8337282995102272, 0.20588758679724872, 0.12522385214612453,
                   0.6390730524643073, 0.7055779213989253, 0.9004255614099713, 0.4075431157767999, 0.161093231584713,
                   0.15250197544465616, 0.7172682822215489, 0.60836236371404, 0.07086628306822396, 0.263719138602719,
                   0.16102036359390437, 0.0065987448849305075, 0.5881312311814277, 0.7836567678399617, 0.9104401158881326,
                   0.8432891635016235, 0.033440093086177236, 0.8514611306363931, 0.2855332934628241, 0.36525972112514427,
                   0.7526593301495519, 0.9963694184200753, 0.5614168317678196, 0.7950126291921057, 0.6212978800904426,
                   0.176936615687169, 0.8817788599562331, 0.13699370230879637, 0.5754950980437555, 0.1507294463182668,
                   0.23409699287029495, 0.6949148063429461, 0.47140569181488556, 0.1470896240551064, 0.8475557222612405,
                   0.05957485472498203, 0.07490903723892406, 0.8412381196460251, 0.26874846387453943, 0.13669341206289243,
                   0.8525684329438777, 0.46716360402752777, 0.8522055745422484, 0.3129394551398561, 0.908966336417204,
                   0.26259461196353984, 0.07245314277889847, 0.41429401839807156, 0.22772860293274222, 0.26662443208488784,
                   0.9875655504027848, 0.5832266083052889, 0.24205847206862052, 0.9843760682096272, 0.16269008279311103,
                   0.4941250734508458, 0.5446841276322587, 0.19222703209695946, 0.9232239752817498, 0.8824688635063289,
                   0.224690851359456, 0.5809304720756304, 0.36863807988348585]

    h2o_glm_random_init = utils_for_glm_hglm_tests.constraint_glm_gridsearch(train, predictors, response, solver="IRLSM",
                                                                        family="binomial",
                                                                        linear_constraints=linear_constraints2,
                                                                        beta_constraints=beta_constraints,
                                                                        startval=random_coef,
                                                                        init_optimal_glm=False,
                                                                        constraint_eta0=constraint_eta0,
                                                                        constraint_tau=constraint_tau,
                                                                        constraint_alpha=constraint_alpha,
                                                                        constraint_beta=constraint_beta,
                                                                        constraint_c0=constraint_c0,
                                                                        return_best=False, epsilon=0.5)
    random_init_logloss = h2o_glm_random_init.model_performance()._metric_json['logloss']
    print("logloss with random GLM coefficient initializaiton: {0}, number of iterations taken to build the model: "
          "{1}".format(random_init_logloss, utils_for_glm_hglm_tests.find_model_iterations(h2o_glm_random_init)))
    print(glm.getConstraintsInfo(h2o_glm_random_init))

    assert logloss <= optimal_init_logloss, "logloss from optimal GLM {0} should be lower than logloss from GLM with light tight" \
                                     " constraints and initialized with optimal GLM {1} but is not.".format(logloss, optimal_init_logloss)

    assert logloss <= default_init_logloss, "logloss from optimal GLM {0} should be lower than logloss from GLM with light tight" \
                                     " constraints and initialized with default coefficients GLM {1} but is " \
                                     "not.".format(logloss, default_init_logloss)

    assert logloss <= random_init_logloss, "logloss from optimal GLM {0} should be lower than logloss from GLM with light tight" \
                                     " constraints and initialized with random coefficients GLM {1} but is " \
                                     "not.".format(logloss, random_init_logloss)
    
if __name__ == "__main__":
    pyunit_utils.standalone_test(test_light_tight_linear_constraints_binomial)
else:
    test_light_tight_linear_constraints_binomial()
