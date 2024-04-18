"""Scale up or down entire Namespaces."""

import kr8s
from loguru import logger


class KubernetesScale:
    """Class for performing scaling operations in an entire namespace."""

    def __init__(self, namespaces: str, replicas: int) -> None:
        """Initialize a new instance of the KubernetesScale class."""
        self.namespaces = namespaces.split(",")
        self.replicas = replicas

    def scale(self) -> None:
        """Scale up or down entire namespaces."""
        for namespace in self.namespaces:
            deployments = kr8s.get("deployments", namespace=namespace)
            for deployment in deployments:
                current_replicas = deployment.spec.replicas
                logger.info(f"Scaling {deployment.metadata.name} in namespace {namespace} from {current_replicas} to {self.replicas}")
                deployment.scale(self.replicas)
