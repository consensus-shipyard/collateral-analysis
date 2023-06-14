# IPC Subnets Collateral Analysis Framework
A collateral analysis framework for subnets that advises on the incentive-compatibility of subnets against a rational adversary given a number of parameters, see the [game-theoretical analysis](https://docs.google.com/document/d/17KQfgiaaNsXPzDRshhMBVyr-gtQX2UmisqwhXdDSwuM/edit#heading=h.bu4uipmv4e42) that supports this program for further information on the calculations here shown.

# Usage 
Currently, the program tolerates command-line arguments, but can also be invoked without any argument (as the program will ask for the remaining paramters if strictly necessary and not provided). It provides 2 recommendations for incentive-compatibility given the rest of the parameters:

## Option 1 - Attackers balance to multiply spend
When selecting this option, the program will calculate, given the rest of the parameters, the maximum adversarial balance for which a subnet with the given parameters ensures the rational adversary will not try to perform an equivocation attack to multiply send. This option is well-suited for subnets to manually configure parameters in order to tolerate a desired adversary.

Example: suppose a set of 100 participants want to create a subnet running the IPC reference implementation such that at least 1000 coins of total collateral must be stored by participants in order for the subnet to be active, and they want to tolerate a rational coalition of up to 49 participants (100/2 - 1), provide immediate finalization of transactions, and allow participants to unstake collateral 3 blocks after the unstaking request. The block production latency is about 1 second. Then:

```
$> python3 collateral-analysis.py -n 100 -q 67 -f 49 -C 1000 -w 3 -t 1 -o 0 -opt 1
With the given parameters, the subnet is incentive-compatible against a rational adversary trying to multiply spend up to 333.905 coins
```

## Option 2 - Finalization delay
When selecting this option, the program will calculate, given the rest of the parameters, the required finalization delay to ensure that the rational adversary will not perform an equivocation attack to multiply spend the provided balance. This balance can be, for example, the sum of the spent balances of a given block, of the balance of a particular transaction. This option gives empowers to applications built on top of IPC subnets with a tool to ensure they tolerate their desired adversary, despite the hardcoded parameters of the subnet.

Example: suppose an application that uses the subnet from the previous example (with the exact same parameters). However, this application deals with large quantities of coins at once (i.e. 10000 instead of 350) and thus it cannot ensure protection against double spends from its transactions by a rational adversary. Then the subnet can instead manually enforce a delayed finalization of a number of blocks:

```
$> python3 collateral-analysis.py -n 100 -q 67 -f 49 -C 1000 -w 3 -t 1 -o 0 -m 10000 -opt 2
With the given parameters, the subnet is incentive-compatible against a rational adversary trying to multiply spend by delaying finalization at least 3 blocks
```

## Option 3 - Adversarial size
Analogously to option 1, this option instructs the program to output, given the rest of the parameters, the maximum adversarial size for which a subnet with the given parameters ensures the rational adversary will not try to perform an equivocation attack to multiply send. This option is well-suited for subnets to manually configure parameters in order to tolerate a desired adversary, or purely for informative purposes for users of the subnet.

Example: suppose a set of 100 participants want to create a subnet running the IPC reference implementation such that at least 330 coins of total collateral must be stored by participants in order for the subnet to be active, and they want to tolerate deviations to multiply spend up to 350 coins, provide immediate finalization of transactions, and allow participants to unstake collateral 3 blocks after the unstaking request. The block production latency is about 1 second. Then:

```
$> python3 collateral-analysis.py -n 100 -q 67 -C 1000 -w 3 -t 1 -o 0 -m 330 -opt 3
With the given parameters, the subnet is incentive-compatible against a rational adversary of size 50 validators (50.0% of the committee)
```
