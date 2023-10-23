"""Package Containing Kubernetes Commands."""

import click


@click.command(name="linkerd")
def linkerd() -> None:
    """Check for the existance of linkerd-proxy sidecars in pods, delete pods without them."""
    from kiroshi.kubernetes.linkerd import KubernetesLinkerd

    KubernetesLinkerd().check()


@click.command(name="scale")
@click.option("--namespaces", required=True, type=str, help="Namespaces to scale, comma separated.")
@click.option("--replicas", required=True, type=int, help="Number of replicas to scale to.")
def scale(namespaces: str, replicas: int) -> None:
    """Scale up or down entire namespaces."""
    from kiroshi.kubernetes.scale import KubernetesScale

    KubernetesScale(namespaces, replicas).scale()
