import random
import matplotlib.pyplot as plt
import sys
import numpy as np
import pandas as pd


class ParticleSwarm:
    def __init__(self, eval_function, dimensions, size, chi=0.729, phi1=2.05, phi2=2.05):
        self.eval_function = eval_function
        self.dimensions = dimensions
        self.size = size
        self.chi = chi
        self.phi1 = phi1
        self.phi2 = phi2
        self.particles = [Particle(self) for _ in range(size)]
        self.best_position = []
        self.best_position_quality = sys.float_info.max

    def run(self, max_iterations=100, stopping_rounds=10, stopping_tolerance=0.001, render=False, as_dataframe=False):
        positions = []
        qualities = []
        iteration = 0
        stop_round_counter = 0
        if as_dataframe:
            lines = []
        while iteration < max_iterations:
            for i in range(self.size):
                self.particles[i].evaluate(self.eval_function)
                if self.particles[i].position_quality < self.best_position_quality:
                    self.best_position = self.particles[i].position.copy()
                    self.best_position_quality = self.particles[i].position_quality

            for i in range(self.size):
                self.particles[i].update_velocity()
                self.particles[i].update_position()

                if as_dataframe:
                    lines.append(self.particles[i].position + [self.particles[i].position_quality, iteration])

            positions.append(self.best_position)
            qualities.append(self.best_position_quality)

            if iteration > 1:
                if abs(qualities[-1] - qualities[-2])/qualities[-2] < stopping_tolerance:
                    stop_round_counter += 1
                else:
                    stop_round_counter = 0

            if stop_round_counter >= stopping_rounds:
                break

            iteration += 1
        if render:
            plt.plot(qualities)

        if as_dataframe:
            df = pd.DataFrame(np.array(lines),
                              columns=[f"x_{i}" for i in range(len(self.dimensions))] + ['quality', 'iteration'])

            return df, qualities, positions

        return qualities, positions


class Particle:
    def __init__(self, swarm):
        self.swarm = swarm
        self.position = [random.uniform(x[0], x[1]) for x in swarm.dimensions]  # random starting position
        self.velocity = [random.uniform(-1, 1) for _ in swarm.dimensions]       # random initial velocity
        self.best_position = []
        self.best_position_quality = sys.float_info.max
        self.position_quality = sys.float_info.max

    def evaluate(self, eval_function):
        self.position_quality = eval_function(self.position)
        if self.position_quality < self.best_position_quality:
            self.best_position = self.position
            self.best_position_quality = self.position_quality

    def update_velocity(self):
        group_best = self.swarm.best_position

        for i in range(len(self.velocity)):
            r1 = random.random()
            r2 = random.random()

            individual_parcel = self.swarm.phi1 * r1 * (self.best_position[i] - self.position[i])
            group_parcel = self.swarm.phi2 * r2 * (group_best[i] - self.position[i])
            self.velocity[i] = self.swarm.chi * (self.velocity[i] + individual_parcel + group_parcel)

    def update_position(self):
        for i in range(len(self.position)):
            self.position[i] = self.position[i] + self.velocity[i]

            dimensions = self.swarm.dimensions
            if self.position[i] > dimensions[i][1]:     # limit position do upper dimensional bounds
                self.position[i] = dimensions[i][1]
            if self.position[i] < dimensions[i][0]:     # limit position do lower dimensional bounds
                self.position[i] = dimensions[i][0]
