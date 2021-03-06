import torch

from src import core


class FeedForwardActor(core.Actor):
    """A feed-forward actor.
    An actor based on a feed-forward policy which takes non-batched observations
    and outputs non-batched actions. It also allows adding experiences to a buffer.

    Attributes:
        policy (func): A mapping that takes an observation from the environment and
            outputs a probability distribution over the action space.
        buffer_client (core.Buffer): A client used to pass observations to the buffer.
        device (torch.device): Determine which device to place observations upon, CPU or GPU.

    # TODO: The actor uses a client in order to add data asynchronously.
    """

    def __init__(self, policy, buffer_client=None, device=torch.device("cpu")):
        """Initialize a FeedForwardActor instance.

        Args:
            policy (func): A function that maps observations from the environment to a
                probability distribution over the action space. The function accepts two
                parameters - an observation and a list of legal actions.
                    `prob = policy(obs, legal)`
                The output of the function is a numpy vector giving probabilities for
                each action of the entire action space. Illegal actions should have a
                probability of 0.
            buffer_client (core.Buffer, optional): A client used to pass observations to
                the buffer. Default value is None, the actor does not save observations.
            device (torch.device, optional): Determine which device to place observations
                upon, CPU or GPU. Default value is "cpu".
        """
        self.policy = policy
        self.buffer_client = buffer_client   # allows to send data to the replay buffer
        self.device = device

    @torch.no_grad()
    def select_action(self, observation, legal=None):
        """Return the action selected by the policy.
        Using the policy function compute a probability distribution over the action space.
        Select the next action by sampling from the probability distribution.

        Args:
            observation (np.Array):A numpy array of shape (state_size,), giving the
                current state of the environment.
            legal (list[int], optional): A list of indices of the legal actions for
                the agent. Default value is None, meaning all actions are legal.

        Returns:
            act (int): The index of the action selected by the policy.
        """
        # Convert the observations to torch tensors and move them to device.
        observation = torch.from_numpy(observation).float()
        observation = observation.to(self.device)

        # Use the policy to compute a probability distribution over the actions and select
        # the next action probabilistically.
        probs = self.policy(observation, legal)
        action = torch.multinomial(probs, 1).squeeze(dim=-1).item()
        return action

    def observe_first(self, timestep):
        """Observe a time-step from the agent-environment interaction loop."""
        if self.buffer_client is not None:
            self.buffer_client.add_first(timestep)

    def observe(self, action, timestep, is_last=False):
        """Observe a time-step from the agent-environment interaction loop."""
        if self.buffer_client is not None:
            self.buffer_client.add(action, timestep, is_last)

#