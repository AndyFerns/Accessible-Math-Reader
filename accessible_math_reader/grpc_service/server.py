"""!
@file grpc_service/server.py
@brief gRPC server implementation for Accessible Math Reader.

@details
Wraps the core ``MathReader`` pipeline in gRPC service handlers.
Reuses the same code paths as the REST API — zero logic duplication.

Requires: ``pip install accessible-math-reader[grpc]``

Start the server:
@code{.bash}
python -m accessible_math_reader.grpc_service.server --port 50051
@endcode

@author Accessible Math Reader Contributors
@version 0.2.0
"""

from __future__ import annotations

import json
import logging
import tempfile
from concurrent import futures
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def serve(port: int = 50051, max_workers: int = 10) -> None:
    """!
    @brief Start the gRPC server.

    @param port         TCP port (default 50051)
    @param max_workers  Thread pool size (default 10)
    """
    try:
        import grpc  # type: ignore[import-untyped]
    except ImportError:
        raise ImportError(
            "grpcio is required. Install with: "
            "pip install accessible-math-reader[grpc]"
        )

    # In a real deployment the generated pb2/pb2_grpc files would be
    # compiled from math_service.proto.  For now, provide a reference
    # implementation using grpc.protos_and_services (requires grpcio-tools).
    #
    # Until protoc is run, this module serves as documentation of the
    # intended server architecture.  The actual servicer is below.
    logger.info("gRPC server starting on port %d (workers=%d)", port, max_workers)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    # TODO: register generated servicer after protoc compilation
    #   math_service_pb2_grpc.add_MathAccessibilityServicer_to_server(
    #       MathAccessibilityServicer(), server
    #   )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info("gRPC server listening on [::]:%d", port)
    server.wait_for_termination()


class MathAccessibilityServicer:
    """!
    @brief gRPC servicer implementing the MathAccessibility service.

    @details
    Each RPC method delegates to ``MathReader`` from the core library.
    This class can be registered with the generated ``add_…Servicer`` once
    the proto is compiled.
    """

    def __init__(self) -> None:
        from accessible_math_reader.reader import MathReader
        self._reader = MathReader()

    def ToSpeech(self, request: Any, context: Any) -> Any:
        """Convert math to speech text."""
        speech = self._reader.to_speech(request.input)
        # Return would be SpeechResponse(speech=speech, input=request.input)
        return {"speech": speech, "input": request.input}

    def ToBraille(self, request: Any, context: Any) -> Any:
        """Convert math to Braille."""
        notation = request.notation or "nemeth"
        braille = self._reader.to_braille(request.input, notation=notation)
        return {"braille": braille, "notation": notation, "input": request.input}

    def GetStructure(self, request: Any, context: Any) -> Any:
        """Return the semantic AST as JSON."""
        structure = self._reader.get_structure(request.input)
        return {"structure_json": json.dumps(structure), "input": request.input}

    def ToAudio(self, request: Any, context: Any) -> Any:
        """Synthesise speech to audio bytes."""
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp_path = tmp.name
        tmp.close()
        self._reader.to_audio(request.input, tmp_path)
        audio_bytes = Path(tmp_path).read_bytes()
        return {"audio_data": audio_bytes, "mime_type": "audio/mpeg"}

    def Validate(self, request: Any, context: Any) -> Any:
        """Run accessibility validation."""
        from accessible_math_reader.validation import MathValidator
        validator = MathValidator()
        return validator.validate_expression(request.input)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AMR gRPC server")
    parser.add_argument("--port", type=int, default=50051)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    serve(port=args.port, max_workers=args.workers)
