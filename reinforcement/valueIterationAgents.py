# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        k = 0
        while k < self.iterations:
            V = util.Counter() # holds k+1 values for all states
            for state in self.mdp.getStates():
                opt_action = self.computeActionFromValues(state) # find optimal action based on V_k
                if opt_action:
                    V[state] = self.computeQValueFromValues(state, opt_action) # find q-value for optimal action in state
            self.values = V
            k += 1


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        q = 0
        for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action): # compute action-state q-value
            q += prob * (self.mdp.getReward(state, action, nextState) + (self.discount * self.getValue(nextState)))

        return q

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        q = util.Counter() # holds q-values for each state-action pair
        for action in self.mdp.getPossibleActions(state): # iterate over each action
            q[action] = self.computeQValueFromValues(state, action)
        return q.argMax()


    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        k = 0
        s = 0
        while k < self.iterations:
            state = self.mdp.getStates()[s]
            opt_action = self.computeActionFromValues(state) # find optimal action based on V_k
            if opt_action:
                self.values[state] = self.computeQValueFromValues(state, opt_action) # find max q-value for given state
            k += 1
            s += 1
            s %= len(self.mdp.getStates())

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        # compute predecessors for all states
        predecessors = {}
        states = []
        for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state):
                states.append(state)
            for action in self.mdp.getPossibleActions(state):
                for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
                    if nextState not in predecessors:
                        predecessors[nextState] = set()
                    predecessors[nextState].add(state)
        # run priority sweep value iteration
        q = util.PriorityQueue()
        k = 0
        while k < self.iterations:
            # populate state priorities based on largest error
            for state in states:
                # find state value
                V = None
                opt_action = self.computeActionFromValues(state) # find optimal action based on V_k
                if opt_action:
                    V = self.computeQValueFromValues(state, opt_action) # find q-value for optimal action in state
                    diff = abs(self.getValue(state) - V)
                    if diff > self.theta or not k:
                        q.update(state, -diff)
            if q.isEmpty():
                break # no states to update, terminate
            # update value (find V_k+1) for prioterized state (with highest error)
            state = q.pop()
            opt_action = self.computeActionFromValues(state) # find optimal action based on V_k
            if opt_action:
                self.values[state] = self.computeQValueFromValues(state, opt_action) # find q-value for optimal action in state
            # update next set of states to sweep
            states = predecessors[state]
            k += 1
