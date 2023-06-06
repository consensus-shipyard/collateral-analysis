from scipy.stats import lognorm
import math
from abc import ABC, abstractmethod
import sys
import argparse

"""
This program is the result of a game-theoretical analysis on collateral for IPC subnets.
For more information on that analysis, see:
https://docs.google.com/document/d/17KQfgiaaNsXPzDRshhMBVyr-gtQX2UmisqwhXdDSwuM/edit#
"""


# Define command-line arguments
parser = argparse.ArgumentParser(description="Program description")
parser.add_argument("-n", type=float, help="Number of members in the committee", default=-1.0)
parser.add_argument("-q", type=float, help="Quorum size", default=-1.0)
parser.add_argument("-f", type=float, help="Rational adversary threshold", default=-1.0)
parser.add_argument("-a", type=float, help="Number of branches in equivocation attack", default=-1.0)
parser.add_argument("-C", type=float, help="Minimum total collateral of the committee", default=-1.0)
parser.add_argument("-c", type=float, help="Minimum collateral per member", default=-1.0)
parser.add_argument("-w", type=float, help="Block delay between unstaking request and actual collateral released", default=-1.0)
parser.add_argument("-o", type=float, help="Transaction finalization delay in number of blocks", default=-1.0)
parser.add_argument("-t", type=float, help="Block production time", default=-1.0)
parser.add_argument("-m", type=float, help="Balance of attackers in equivocation attack", default=-1.0)
parser.add_argument("-dist", type=float, help="(UNUSED FOR NOW) Select option of message delay distribution (currently only lognormal with mu=-1.0, sigma=1)", default=-1.0)

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

def retrieve_dist():
    mu = -1.0
    sigma = 1.0
    return LogNormalDistribution(mu=mu, sigma=sigma)

def retrieve_n():
    args = parser.parse_args()
    if args.n >= 0:
        return args.n
    else:
        return float(input("Enter the number of players in the committee: "))

def retrieve_q():
    args = parser.parse_args()
    if args.q >= 0:
        return args.q
    else:
        return float(input("Enter the quorum size: "))


def retrieve_f():
    args = parser.parse_args()
    if args.f >= 0:
        return args.f
    else:
        return float(input("Enter the rational adversary threshold: "))

def retrieve_a(needed:bool):
    args = parser.parse_args()
    if args.a >= 0:
        return args.a
    elif needed:
        return float(input("Enter the number of branches in equivocation attack: "))
    return 0

def retrieve_C(needed:bool):
    args = parser.parse_args()
    if args.C >= 0:
        return args.C
    elif needed:
        return float(input("Enter the minimum total collateral: "))
    return 0

def retrieve_c(needed:bool):
    args = parser.parse_args()
    if args.c >= 0:
        return args.c
    elif needed:
        return float(input("Enter the minimum collateral per player: "))
    return 0

def retrieve_w():
    args = parser.parse_args()
    if args.w >= 0:
        return args.w
    else:
        return float(input("Enter the block delay between unstaking request and actual collateral released "))

def retrieve_omega():
    args = parser.parse_args()
    if args.o >= 0:
        return args.o
    else:
        return float(input("Enter the transaction finalization delay in number of blocks: "))

def retrieve_t():
    args = parser.parse_args()
    if args.t >= 0:
        return args.t
    else:
        return float(input("Enter the block production time (in seconds): "))

def retrieve_m():
    args = parser.parse_args()
    if args.m >= 0:
        return args.m
    else:
        return float(input("Enter the balance of attackers in equivocation attack: "))

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

    option = starting_menu()
    if option == "1":
        dist = retrieve_dist()
        n = retrieve_n()
        q = retrieve_q()
        f = retrieve_f()
        a = retrieve_a(False)

        if a == 0:
            a = fork_max_branches(n, q, f)
            if a == 1:
                sys.exit("The adversary is not big enough to equivocate given the quorum size")

        C = retrieve_C(False)

        needed = False
        if C==0:
            needed = True

        c = retrieve_c(needed)
        C = collateral_lower_bound(C, c, n)

        w_blocks = retrieve_w()
        blocktime = retrieve_t()
        w = blocktime * w_blocks

        omega_blocks = retrieve_omega()
        omega = omega_blocks*blocktime

        c = C/n
        slashable_collateral = minimum_adversary(a, n, q)*c
        m = maximum_safe_spend(a, slashable_collateral, w, omega, dist)
        print("With the given parameters, the subnet is incentive-compatible against an attack that equivocates into {} branches with {:.3f} coins".format(a, m))
    elif option == "2":
        sys.exit("Invalid option {} selected".format(option))
    else:
        sys.exit("Invalid option {} selected".format(option))

def starting_menu():
    print("Select the parameter to recommend for incentive-compatibility against equivocation attack")
    print("1. Attackers balance to multiply spend")
    print("2. Transaction/block finalization delay")
    return input("Your option: ")

def op1_parameters():
    # If no, then draw from the default libp2p measurements lognormal mu=-1.0 sigma=1.0


    return dist, n, q, f, max_a, C, w, omega

if __name__ == "__main__":
    main()
