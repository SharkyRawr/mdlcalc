class Mdlcalc < Formula
  include Language::Python::Virtualenv

  desc "Calculate approximate memory requirements for LLM inference"
  homepage "https://github.com/SharkyRawr/mdlcalc"
  url "https://github.com/SharkyRawr/mdlcalc/archive/refs/tags/main.tar.gz"
  sha256 "ff1dc5457f30ff5a1f43cdbc99cacd69d5d4e9d6bf66c6a2a7999784704a279d"
  license "CC-BY-NC-SA-4.0"

  depends_on "python@3.12"

  resource "click" do
    url "https://github.com/SharkyRawr/mdlcalc/archive/refs/tags/main.tar.gz"
    sha256 "ff1dc5457f30ff5a1f43cdbc99cacd69d5d4e9d6bf66c6a2a7999784704a279d"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Q4_K_M", shell_output("#{bin}/mdlcalc 7B")
    assert_match "GB", shell_output("#{bin}/mdlcalc 1T Q8_0")
  end
end
