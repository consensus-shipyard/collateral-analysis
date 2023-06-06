from scipy.stats import lognorm
import math
from abc import ABC, abstractmethod

"""
This program is the result of a game-theoretical analysis on collateral for IPC subnets.
For more information on that analysis, see:
https://docs.google.com/document/d/17KQfgiaaNsXPzDRshhMBVyr-gtQX2UmisqwhXdDSwuM/edit#
"""



class RandomDistribution(ABC):
    @abstractmethod
    def cdf(self, x):
        pass

class LogNormalDistribution(RandomDistribution):
    def __init__(self, mu, sigma):
        self.mu = mu
        self.sigma = sigma

    def cdf(self, x):
        return lognorm.cdf(x, s=self.sigma, scale=math.exp(self.mu))

# returns the maximum number of branches that can be performed by an attacker of that power
def fork_max_branches(n, q, f):
    a = (n - f) / (q - f)
    return int(a)

# returns the minimum adversary that can perform a multiple spending attack with a branches 
def minimum_adversary(a, n, q):
    f = (a*q-n)/(a-1)
    return int(f)

# If expected_total_loss is positive, that means that attackers will lose that amount in expectation from performing the attack with the provided parameters. If it is negative, the attackers will win the absolute value of that amount in expectation.
def expected_total_loss(a, C, m, w, omega, x_dist: RandomDistribution):
    p_x_greater_w = 1 - x_dist.cdf(w)
    p_omega_less_x_greater_w = x_dist.cdf(w) - x_dist.cdf(omega)

    value = C + p_x_greater_w * (m * (1 - a) - C) - (a - 1) * p_omega_less_x_greater_w * m

    return value

# maximum_safe_spend returns the maximum amount that the attackers would not multiply spend 
# as they would in expectation lose more than they win
def maximum_safe_spend(a, C, w, omega, x_dist: RandomDistribution):
    return x_dist.cdf(w)/(a-1)*C

def collateral_lower_bound(total_collateral, collateral, n):
    if int(total_collateral) == 0:
        return collateral*n
    if int(collateral) == 0:
        return total_collateral 

    return max(total_collateral, collateral*n)

def main():
    dist, n, q, f, max_a, C, w, omega = parameters_from_input() #default_parameters_example1()

    c = C/n
    slashable_collateral = minimum_adversary(max_a, n, q)*c #the hardest scenario is for max_a
    m = maximum_safe_spend(max_a, slashable_collateral, w, omega, dist)
    print("With the given parameters, the subnet is incentive-compatible against an attack that equivocates into {} branches with {:.3f} coins".format(max_a, m))

def parameters_from_input():
    # If no, then draw from the default libp2p measurements lognormal mu=-1.0 sigma=1.0
    distr_input = input("Would you like to follow the recommended message delay distribution (Y/n) ")
    if distr_input == 'n':
        print("We do not tolerate any other distribution for the moment")
        exit

    mu = -1.0
    sigma = 1.0
    dist = LogNormalDistribution(mu=mu, sigma=sigma)

    # At the moment, we assume no committee rotation (full participation)
    n = float(input("Enter the number of players in the committee: "))
    q = float(input("Enter the quorum size q \in ({},{}]: ".format(int(n/2),int(n))))
    f = float(input("Enter the rational adversary that should be tolerated f \in [0,{}): ".format(int(q))))
    max_a = fork_max_branches(n, q, f)
    if max_a == 1:
        print("That adversary is not big enough to double-spend given the quorum size: ")
        exit

    print("The size of this rational adversary means it can equivocate into up to {} distinct blocks in one iteration".format(max_a))

    total_collateral_input = float(input("Enter the minimum total collateral: "))
    collateral_input = float(input("Enter the minimum collateral per process: "))

    C = collateral_lower_bound(total_collateral_input, collateral_input, n)

    w_blocks = float(input("Enter the number of blocks between when a request to retrieve collateral is written in the parent subnet and when it is executed to unstake the collateral: "))
    blocktime = float(input("Enter the expected block production time of the subnet (in seconds) "))

    w = blocktime * w_blocks

    omega_blocks = float(input("Enter the number of blocks for an application to consider a transaction in the subnet as final (0 if immediate): "))

    omega = omega_blocks*blocktime

    return dist, n, q, f, max_a, C, w, omega

def default_parameters_example1():
    return LogNormalDistribution(mu=-1.0, sigma=1.0), 100, 67, 66, 34, 1000, 3, 0

if __name__ == "__main__":
    main()
