"""SSH compatibility helpers for older Cisco IOS lab images."""

from __future__ import annotations


LEGACY_IOS_KEX_ALGORITHMS = (
    "diffie-hellman-group14-sha1",
    "diffie-hellman-group-exchange-sha1",
    "diffie-hellman-group1-sha1",
)


def enable_legacy_ios_kex() -> None:
    """Allow Paramiko to negotiate SSH KEX with old IOSvL2 images.

    Some IOSvL2 lab images only offer SHA1-based Diffie-Hellman KEX. Paramiko
    4+ removes these algorithms, so the dependency must also be pinned to a
    Paramiko 3.x release that still contains them.
    """
    try:
        import paramiko
    except ImportError:
        return

    transport = paramiko.Transport
    kex_info = getattr(transport, "_kex_info", {})
    missing = [name for name in LEGACY_IOS_KEX_ALGORITHMS if name not in kex_info]
    if missing:
        version = getattr(paramiko, "__version__", "unknown")
        raise RuntimeError(
            "This Cisco IOSvL2 SSH server only offers legacy SHA1 KEX algorithms, "
            f"but Paramiko {version} does not support them. Run "
            "`python -m pip install 'paramiko<4'` inside the project virtual "
            "environment, then try again."
        )

    preferred_kex = tuple(getattr(transport, "_preferred_kex", ()))
    if not preferred_kex:
        return

    enabled_kex = preferred_kex + tuple(
        name for name in LEGACY_IOS_KEX_ALGORITHMS if name not in preferred_kex
    )
    transport._preferred_kex = enabled_kex
