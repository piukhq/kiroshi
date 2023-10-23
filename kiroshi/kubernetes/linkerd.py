"""Checks pods in all namespaces have linkerd-proxy sidecars if configured to have them."""

import kr8s
from loguru import logger


class KubernetesLinkerd:
    """Class for checking the existance of linkerd-proxy sidecars in pods."""

    def __init__(self) -> None:
        """Initialize the KubernetesLinkerd class."""

    def check(self) -> None:
        """Check for the existance of linkerd-proxy sidecars in pods, delete pods without them."""
        pods = kr8s.get("pods", namespace=kr8s.ALL)
        for pod in pods:
            if "linkerd.io/inject" in pod.annotations and not next(
                (container for container in pod.spec.containers if container.name == "linkerd-proxy"), None
            ):
                logger.info(
                    f"linkerd missing in pod {pod.metadata.name} in namespace {pod.metadata.namespace}, deleting"
                )
                pod.delete()
