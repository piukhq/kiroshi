"""Checks pods in all namespaces have linkerd-proxy sidecars if configured to have them."""

import kr8s
from loguru import logger


class KubernetesLinkerd:
    """Class for checking the existance of linkerd-proxy sidecars in pods."""

    def __init__(self) -> None:
        """Initialize the KubernetesLinkerd class."""

    def check(self) -> None:
        """Check if linkerd annotation is present, if so, check linkerd-proxy is present and at the correct version."""
        linkerd_version = kr8s.get("pods", namespace="linkerd")[0].spec.containers[0].image.split(":")[1]
        pods = kr8s.get("pods", namespace=kr8s.ALL)
        logger.info(f"Linkerd version: {linkerd_version}")
        for pod in pods:
            logger.info(f"Checking pod {pod.metadata.name} in namespace {pod.metadata.namespace}")
            if "linkerd.io/inject" in pod.annotations:
                container = next(
                    (container for container in pod.spec.containers if container.name == "linkerd-proxy"), None
                )
                if not container:
                    logger.warning(
                        f"linkerd-proxy not present in pod {pod.metadata.name} in namespace {pod.metadata.namespace}, deleting pod"
                    )
                    pod.delete()
                if container:
                    pod_linkerd_version = container.image.split(":")[1]
                    if pod_linkerd_version != linkerd_version:
                        logger.warning(
                            f"linkerd-proxy version {pod_linkerd_version} in pod {pod.metadata.name} in namespace {pod.metadata.namespace} does not match linkerd version {linkerd_version}, deleting pod"
                        )
                        pod.delete()
