import subprocess
from typing import Dict, Any, Tuple, List

def _run(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a subprocess and return (code, stdout, stderr)."""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    return proc.returncode, out.strip(), err.strip()

def get_container_name(slug: str) -> str:
    return f"apphost_{slug}"

def ensure_image(app_data: Dict[str, Any]) -> str:
    """Ensure image is available.

    Supports:
      mode = 'pull'  -> docker pull
      mode = 'build' -> docker build -t apphost_<slug> <context>
    """
    slug = app_data["slug"]
    container = app_data.get("container", {}) or {}
    mode = container.get("mode", "pull")
    image = container.get("image")
    build_context = container.get("build_context", ".")

    if mode == "build":
        image = image or get_container_name(slug)
        code, out, err = _run(["docker", "build", "-t", image, build_context])
        if code != 0:
            raise RuntimeError(f"docker build failed: {err or out}")
        return image

    if not image:
        raise RuntimeError("container.image is required for mode 'pull'")

    code, out, err = _run(["docker", "pull", image])
    if code != 0:
        # non-fatal; maybe image is local only
        pass
    return image

def ensure_container_running(app_data: Dict[str, Any]) -> int:
    """Ensure container for this app is running.

    Returns host_port used for HTTP.
    """
    slug = app_data["slug"]
    container = app_data.get("container", {}) or {}
    host_port = int(container.get("host_port", 0))
    internal_port = int(container.get("internal_port", 8000))
    if not host_port:
        raise RuntimeError("container.host_port must be set for container apps.")

    name = get_container_name(slug)

    # Check if container is already running
    code, out, err = _run(["docker", "ps", "--filter", f"name={name}", "--format", "{{.Names}}"])
    if code == 0 and name in out.splitlines():
        return host_port

    # Stop + remove existing container with same name (if any)
    _run(["docker", "rm", "-f", name])

    image = ensure_image(app_data)

    env_vars = []
    env_spec = container.get("env", "")
    if isinstance(env_spec, str):
        for line in env_spec.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            env_vars.extend(["-e", line])
    elif isinstance(env_spec, dict):
        for k, v in env_spec.items():
            env_vars.extend(["-e", f"{k}={v}"])

    # Optional data mount
    volume_args = []
    data_dir = container.get("data_dir")
    if data_dir:
        volume_args = ["-v", f"{data_dir}:/data"]

    cmd = [
        "docker", "run", "-d",
        "--name", name,
        "-p", f"127.0.0.1:{host_port}:{internal_port}",
        "--restart", "always",
        *env_vars,
        *volume_args,
        image,
    ]
    code, out, err = _run(cmd)
    if code != 0:
        raise RuntimeError(f"docker run failed: {err or out}")
    return host_port
