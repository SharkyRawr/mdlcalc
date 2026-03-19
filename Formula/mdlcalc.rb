class Mdlcalc < Formula
  include Language::Python::Virtualenv

  desc "Calculate approximate memory requirements for LLM inference"
  homepage "https://github.com/SharkyRawr/mdlcalc"
  url "https://github.com/SharkyRawr/mdlcalc/releases/download/v0.1.1/mdlcalc-0.1.0-py3-none-any.whl"
  sha256 "91e822fbd3291cd60fdd5c12376022e6eb6e3b2d05e6d2d8a98f24ccd778a233"
  license "CC-BY-NC-SA-4.0"

  depends_on "python@3.12"

  def install
    venv = virtualenv_create(libexec, "python3.12")
    venv.pip_install_and_link buildpath
  end

  test do
    assert_match "Q4_K_M", shell_output("#{bin}/mdlcalc 7B")
    assert_match "GB", shell_output("#{bin}/mdlcalc 1T Q8_0")
  end
end
