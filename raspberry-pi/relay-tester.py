#!/usr/bin/env python3

"""Simple relay pin tester for Raspberry Pi.

Cycles through the four relay pins used by the MASH IoT project, turning each
relay on for a configurable interval before moving to the next one. Designed
for manual troubleshooting and hardware verification.
"""

import argparse
import time
from itertools import combinations
from typing import Iterable, Optional, Tuple

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:  # pragma: no cover - allows running on non-Pi machines
    GPIO_AVAILABLE = False

# BCM pin numbers mapped to human-friendly labels
RELAY_PINS: Tuple[Tuple[str, int], ...] = (
    ("Blower Fan", 22),
    ("Exhaust Fan", 27),
    ("Humidifier", 17),
    ("LED Lights", 18),
)

ACTUATOR_OPTIONS_HELP = "; ".join(
    f"{idx}: {label} (GPIO {pin})"
    for idx, (label, pin) in enumerate(RELAY_PINS, start=1)
)


def parse_target_argument(value: str) -> Tuple[int, ...]:
    """Convert CLI actuator selection into tuple of actuator indices."""

    tokens = [token.strip() for token in value.replace(",", "+").split("+") if token.strip()]
    if not tokens:
        raise argparse.ArgumentTypeError("Selection cannot be empty.")

    indexes = []
    for token in tokens:
        if token.isdigit():
            idx = int(token)
            if not 1 <= idx <= len(RELAY_PINS):
                raise argparse.ArgumentTypeError(
                    f"Actuator number '{token}' is out of range. Valid options: {ACTUATOR_OPTIONS_HELP}."
                )
            indexes.append(idx - 1)
            continue

        # Allow matching by actuator name prefix (case-insensitive)
        lowered = token.lower()
        matches = [i for i, (label, _) in enumerate(RELAY_PINS) if label.lower().startswith(lowered)]
        if not matches:
            raise argparse.ArgumentTypeError(
                f"Unknown actuator '{token}'. Valid options: {ACTUATOR_OPTIONS_HELP}."
            )
        if len(matches) > 1:
            raise argparse.ArgumentTypeError(
                f"Selection '{token}' is ambiguous; be more specific. Choices: {ACTUATOR_OPTIONS_HELP}."
            )
        indexes.append(matches[0])

    unique_indexes = []
    seen = set()
    for idx in indexes:
        if idx not in seen:
            unique_indexes.append(idx)
            seen.add(idx)

    return tuple(unique_indexes)


def setup_gpio(pins: Iterable[int]) -> None:
    """Initialise GPIO outputs for relay testing."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # Active-low relays: HIGH keeps them off


def cleanup_gpio(pins: Iterable[int]) -> None:
    """Reset relay outputs and release GPIO resources."""
    for pin in pins:
        GPIO.output(pin, GPIO.HIGH)
    GPIO.cleanup()


def set_relays_active(active_pins: Iterable[int]) -> None:
    """Drive active-low relays so only selected pins are energised."""
    active_set = set(active_pins)
    for _, pin in RELAY_PINS:
        GPIO.output(pin, GPIO.LOW if pin in active_set else GPIO.HIGH)


def run_cycle(
    interval: float,
    pause: float,
    once: bool,
    targets: Optional[Iterable[Tuple[int, ...]]],
    steady: bool,
) -> None:
    """Toggle relays in single and grouped combinations."""
    pins = [pin for _, pin in RELAY_PINS]

    if GPIO_AVAILABLE:
        setup_gpio(pins)
        set_relays_active([])
    else:
        print("RPi.GPIO not available - running in simulation mode.")

    if targets:
        combo_sequence = [
            tuple(RELAY_PINS[idx] for idx in combo)
            for combo in targets
        ]
    elif not steady:
        combo_sequence = []
        for group_size in range(1, len(RELAY_PINS) + 1):
            combo_sequence.extend(combinations(RELAY_PINS, group_size))
    else:
        combo_sequence = [tuple(RELAY_PINS)]

    print("Actuator map:")
    for idx, (label, pin) in enumerate(RELAY_PINS, start=1):
        print(f"  {idx}: {label} (GPIO {pin})")

    if steady:
        steady_combo = combo_sequence[0]
        labels = ", ".join(label for label, _ in steady_combo)
        active = [pin for _, pin in steady_combo]
        print(f"Holding {labels} (pins {', '.join(map(str, active))}) until interrupted...")
        try:
            if GPIO_AVAILABLE:
                set_relays_active(active)
            while True:
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nSteady relay hold interrupted by user.")
        finally:
            if GPIO_AVAILABLE:
                cleanup_gpio(pins)
            print("GPIO cleanup complete.")
        return

    try:
        while True:
            for combo in combo_sequence:
                labels = ", ".join(label for label, _ in combo)
                active = [pin for _, pin in combo]
                print(f"Activating {labels} (pins {', '.join(map(str, active))})")
                if GPIO_AVAILABLE:
                    set_relays_active(active)
                time.sleep(interval)

                print(f"Deactivating {labels}")
                if GPIO_AVAILABLE:
                    set_relays_active([])
                time.sleep(pause)

            if once:
                break
    except KeyboardInterrupt:
        print("\nRelay test interrupted by user.")
    finally:
        if GPIO_AVAILABLE:
            cleanup_gpio(pins)
        print("GPIO cleanup complete.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cycle relay pins for testing.")
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds to hold each relay on (default: 5).",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=1.0,
        help="Seconds to wait after turning a relay off (default: 1).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single pass through the relay list instead of looping.",
    )
    parser.add_argument(
        "-t",
        "--targets",
        nargs="+",
        type=parse_target_argument,
        help=(
            "Specify actuator numbers or name prefixes to activate. "
            "Use '+' or ',' to combine (e.g. '1+2 3'). "
            f"Available: {ACTUATOR_OPTIONS_HELP}."
        ),
    )
    parser.add_argument(
        "--steady",
        action="store_true",
        help="Keep the selected actuators energised until interrupted (requires --targets).",
    )
    args = parser.parse_args()
    if args.steady and not args.targets:
        parser.error("--steady requires at least one selection via --targets.")
    return args


def main() -> None:
    args = parse_args()
    run_cycle(
        interval=args.interval,
        pause=args.pause,
        once=args.once,
        targets=args.targets,
        steady=args.steady,
    )


if __name__ == "__main__":
    main()
