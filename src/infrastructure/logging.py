import numpy as np
import torch
import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle
import os

class NullLogger:

    def add_mean_Q(self, agent):
        pass

    def add_return(self, agent, G):
        pass

    def add_episode_length(self, agent, L):
        pass

    def add_buffer_capacity(self, agent, capacity):
        pass

    def add_Q_network(self, agent, network):
        pass


class DQNAgentLogger:

    def __init__(self, output_dir):
        self.output_dir = output_dir
        self._n_param = 1
        self._mean_Q_values = []
        self._episode_returns = []
        self._episode_lengths = []
        self._experience_capacity = []
        self._total_experiences = 0

    def add_mean_Q(self, agent):
        qvalues = []
        net = agent._learner.Qnetwork
        device = net.device
        with torch.no_grad():
            for _ in range(10):
                batch = agent._buffer.draw(512)
                states = np.array([x.current for x in batch], dtype=np.float32)
                states = torch.from_numpy(states).to(device)
                Qvals = net(states)
                qvalues.append(Qvals.cpu().numpy())
        self._mean_Q_values.append(np.mean(qvalues))
        filename_figure = os.path.join(self.output_dir, 'mean-Q.pdf')
        filename_pickle = os.path.join(self.output_dir, 'mean-Q.pickle')
        with open(filename_pickle, mode='wb') as f:
            pickle.dump(self._mean_Q_values, f)
        self.plot_line(filename_figure, self._mean_Q_values)

    def add_return(self, agent, G):
        self._episode_returns.append(G)
        filename_figure = os.path.join(self.output_dir, 'mean-return.pdf')
        filename_pickle = os.path.join(self.output_dir, 'returns.pickle')
        with open(filename_pickle, mode='wb') as f:
            pickle.dump(self._episode_returns, f)
        mu = np.convolve(self._episode_returns, np.ones(10), 'valid') / 10.0
        self.plot_line(filename_figure, mu)

    def add_episode_length(self, agent, L):
        self._episode_lengths.append(L)
        self._total_experiences += L
        filename_figure = os.path.join(self.output_dir, 'episode-lengths.pdf')
        filename_txt = os.path.join(self.output_dir, 'total_experiences.txt')
        filename_pickle = os.path.join(self.output_dir, 'episode-lengths.pickle')
        with open(filename_txt, mode='w') as f:
            f.writelines([f'Total Experiences: {self._total_experiences}\n'])
        with open(filename_pickle, mode='wb') as f:
            pickle.dump(self._episode_lengths, f)
        mu = np.convolve(self._episode_lengths, np.ones(10), 'valid') / 10.0
        self.plot_line(filename_figure, mu)

    def add_buffer_capacity(self, agent, capacity):
        # self._experience_capacity.append(capacity)
        filename = os.path.join(self.output_dir, 'experience-capacity.txt')
        with open(filename, mode='w') as f:
            f.writelines([f'Buffer capacity: {capacity}\n'])

    def add_Q_network(self, agent, Qnet):
        filename = f'parameters_{self._n_param}.torch'
        Qnet.save(os.path.join(self.output_dir, filename))
        self._n_param += 1

    def plot_line(self, filename, *plot_args, **plot_kwargs):
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(*plot_args, **plot_kwargs)
        fig.savefig(filename)
        plt.close(fig)
