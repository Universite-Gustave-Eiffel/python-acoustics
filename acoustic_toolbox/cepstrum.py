"""The cepstrum module contains functions for cepstral analysis of signals.

Functions:
  complex_cepstrum: Compute the complex cepstrum of a real sequence.
  real_cepstrum: Compute the real cepstrum of a real sequence.
  inverse_complex_cepstrum: Compute the inverse complex cepstrum of a real sequence.
  minimum_phase: Compute the minimum phase reconstruction of a real sequence.

Notes:
  The cepstrum is defined as the inverse Fourier transform of the logarithm of the
  Fourier transform of a signal. It has applications in speech processing, echo detection,
  and signal deconvolution.
"""

import numpy as np
from numpy.typing import NDArray
from typing import Tuple, Optional

__all__ = [
    "complex_cepstrum",
    "real_cepstrum",
    "inverse_complex_cepstrum",
    "minimum_phase",
]


def complex_cepstrum(
    x: NDArray[np.float64], n: Optional[int] = None
) -> Tuple[NDArray[np.float64], NDArray[np.int_]]:
    r"""Compute the complex cepstrum of a real sequence.

    The complex cepstrum is given by:
    $$
    c[n] = F^{-1}\left[\log_{10}\left(F{x[n]}\right)\right]
    $$

    where $x[n]$ is the input signal and $F$ and $F^{-1}$
    are respectively the forward and backward Fourier transform.


    Args:
      x: Real sequence to compute complex cepstrum of.
      n: Length of the Fourier transform.

    Returns:
      The complex cepstrum of the real data sequence `x` computed using the Fourier transform.
      The amount of samples of circular delay added to `x`.


    See Also:
      - [`real_cepstrum`][acoustic_toolbox.cepstrum.real_cepstrum]: Compute the real cepstrum.
      - [`inverse_complex_cepstrum`][acoustic_toolbox.cepstrum.inverse_complex_cepstrum]: Compute the inverse complex cepstrum of a real sequence.

    Examples:
      In the following example we use the cepstrum to determine the fundamental
      frequency of a set of harmonics. There is a distinct peak at the quefrency
      corresponding to the fundamental frequency. To be more precise, the peak
      corresponds to the spacing between the harmonics.

      >>> import numpy as np
      >>> import matplotlib.pyplot as plt
      >>> from acoustic_toolbox.cepstrum import complex_cepstrum

      >>> duration = 5.0
      >>> fs = 8000.0
      >>> samples = int(fs*duration)
      >>> t = np.arange(samples) / fs

      >>> fundamental = 100.0
      >>> harmonics = np.arange(1, 30) * fundamental
      >>> signal = np.sin(2.0*np.pi*harmonics[:,None]*t).sum(axis=0)
      >>> ceps, _ = complex_cepstrum(signal)

      >>> fig = plt.figure()
      >>> ax0 = fig.add_subplot(211)
      >>> ax0.plot(t, signal)
      >>> ax0.set_xlabel('time in seconds')
      >>> ax0.set_xlim(0.0, 0.05)
      >>> ax1 = fig.add_subplot(212)
      >>> ax1.plot(t, ceps)
      >>> ax1.set_xlabel('quefrency in seconds')
      >>> ax1.set_xlim(0.005, 0.015)
      >>> ax1.set_ylim(-5., +10.)

    References:
      1. Wikipedia, "Cepstrum".
            [http://en.wikipedia.org/wiki/Cepstrum](http://en.wikipedia.org/wiki/Cepstrum)
      2. M.P. Norton and D.G. Karczub, D.G.,
            "Fundamentals of Noise and Vibration Analysis for Engineers", 2003.
      3. B. P. Bogert, M. J. R. Healy, and J. W. Tukey:
            "The Quefrency Analysis of Time Series for Echoes: Cepstrum, Pseudo
            Autocovariance, Cross-Cepstrum and Saphe Cracking".
            Proceedings of the Symposium on Time Series Analysis
            Chapter 15, 209-243. New York: Wiley, 1963.
    """

    def _unwrap(
        phase: NDArray[np.float64],
    ) -> Tuple[NDArray[np.float64], NDArray[np.int_]]:
        """Unwrap phase values.

        Args:
          phase: Phase values to unwrap.

        Returns:
          Unwrapped phase values
          Number of delay samples
        """
        samples = phase.shape[-1]
        unwrapped = np.unwrap(phase)
        center = (samples + 1) // 2
        if samples == 1:
            center = 0
        ndelay = np.array(np.round(unwrapped[..., center] / np.pi))
        unwrapped -= np.pi * ndelay[..., None] * np.arange(samples) / center
        return unwrapped, ndelay

    spectrum = np.fft.fft(x, n=n)
    unwrapped_phase, ndelay = _unwrap(np.angle(spectrum))
    log_spectrum = np.log(np.abs(spectrum)) + 1j * unwrapped_phase
    ceps = np.fft.ifft(log_spectrum).real

    return ceps, ndelay


def real_cepstrum(
    x: NDArray[np.float64], n: Optional[int] = None
) -> NDArray[np.float64]:
    r"""Compute the real cepstrum of a real sequence.

    The real cepstrum is given by:
    $$
    c[n] = F^{-1}\left[\log_{10}\left|F{x[n]}\right|\right]
    $$

    where $x[n]$ is the input signal and $F$ and $F^{-1}$ are respectively
    the forward and backward Fourier transform.

    Note that contrary to the complex cepstrum the magnitude is taken of the spectrum.

    Args:
      x: Real sequence to compute real cepstrum of.
      n: Length of the Fourier transform.

    Returns:
      The real cepstrum.


    See Also:
      - [`complex_cepstrum`][acoustic_toolbox.cepstrum.complex_cepstrum]: Compute the complex cepstrum of a real sequence.
      - [`inverse_complex_cepstrum`][acoustic_toolbox.cepstrum.inverse_complex_cepstrum]: Compute the inverse complex cepstrum of a real sequence.

    Examples:
      >>> from acoustic_toolbox.cepstrum import real_cepstrum

    References:
      1. Wikipedia, "Cepstrum".
          [http://en.wikipedia.org/wiki/Cepstrum](http://en.wikipedia.org/wiki/Cepstrum)
    """
    spectrum = np.fft.fft(x, n=n)
    ceps = np.fft.ifft(np.log(np.abs(spectrum))).real

    return ceps


def inverse_complex_cepstrum(
    ceps: NDArray[np.float64], ndelay: NDArray[np.int_]
) -> NDArray[np.float64]:
    r"""Compute the inverse complex cepstrum of a real sequence.

    The inverse complex cepstrum is given by:
    $$
    x[n] = F^{-1}\left[\exp(F(c[n]))\right]
    $$

    where $c[n]$ is the input signal and $F$ and $F^{-1}$ are respectively the forward and backward Fourier transform.

    Args:
      ceps: Real sequence to compute inverse complex cepstrum of.
      ndelay: The amount of samples of circular delay added to `x`.

    Returns:
      The inverse complex cepstrum of the real sequence `ceps`.

    See Also:
      - [`complex_cepstrum`][acoustic_toolbox.cepstrum.complex_cepstrum]: Compute the complex cepstrum of a real sequence.
      - [`real_cepstrum`][acoustic_toolbox.cepstrum.real_cepstrum]: Compute the real cepstrum of a real sequence.

    Examples:
      Taking the complex cepstrum and then the inverse complex cepstrum results
      in the original sequence.

      >>> import numpy as np
      >>> from acoustic_toolbox.cepstrum import inverse_complex_cepstrum
      >>> x = np.arange(10)
      >>> ceps, ndelay = complex_cepstrum(x)
      >>> y = inverse_complex_cepstrum(ceps, ndelay)
      >>> print(x)
      >>> print(y)

    References:
      1. Wikipedia, "Cepstrum".
          [http://en.wikipedia.org/wiki/Cepstrum](http://en.wikipedia.org/wiki/Cepstrum)
    """

    def _wrap(
        phase: NDArray[np.float64], ndelay: NDArray[np.int_]
    ) -> NDArray[np.float64]:
        """Wrap phase values.

        Args:
          phase: Phase values to wrap.
          ndelay: Number of delay samples.

        Returns:
          Wrapped phase values.
        """
        ndelay = np.array(ndelay)
        samples = phase.shape[-1]
        center = (samples + 1) // 2
        wrapped = phase + np.pi * ndelay[..., None] * np.arange(samples) / center
        return wrapped

    log_spectrum = np.fft.fft(ceps)
    spectrum = np.exp(log_spectrum.real + 1j * _wrap(log_spectrum.imag, ndelay))
    x = np.fft.ifft(spectrum).real
    return x


def minimum_phase(
    x: NDArray[np.float64], n: Optional[int] = None
) -> NDArray[np.float64]:
    """Compute the minimum phase reconstruction of a real sequence.

    Args:
      x: Real sequence to compute the minimum phase reconstruction of.
      n: Length of the Fourier transform.

    Returns:
      The minimum phase reconstruction of the real sequence `x`.

    Compute the minimum phase reconstruction of a real sequence using the real cepstrum.

    See Also:
      - [`real_cepstrum`][acoustic_toolbox.cepstrum.real_cepstrum]: Compute the real cepstrum.

    Examples:
      >>> from acoustic_toolbox.cepstrum import minimum_phase

    References:
      1. Soo-Chang Pei, Huei-Shan Lin. Minimum-Phase FIR Filter Design Using
          Real Cepstrum. IEEE TRANSACTIONS ON CIRCUITS AND SYSTEMS-II:
          EXPRESS BRIEFS, VOL. 53, NO. 10, OCTOBER 2006
    """
    if n is None:
        n = len(x)
    ceps = real_cepstrum(x, n=n)
    odd = n % 2
    window = np.concatenate(
        (
            [1.0],
            2.0 * np.ones((n + odd) // 2 - 1),
            np.ones(1 - odd),
            np.zeros((n + odd) // 2 - 1),
        )
    )

    m = np.fft.ifft(np.exp(np.fft.fft(window * ceps))).real

    return m
