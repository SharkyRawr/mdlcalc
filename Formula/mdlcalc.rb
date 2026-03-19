class Mdlcalc < Formula
  desc "Calculate approximate memory requirements for LLM inference"
  homepage "https://github.com/SharkyRawr/mdlcalc"
  url "https://github.com/SharkyRawr/mdlcalc/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "PLACEHOLDER"
  license "CC-BY-NC-SA-4.0"

  depends_on "python@3.12"

  resource "click" do
    url "https://files.pythonhosted.org/packages/source/c/click/click-8.2.1.tar.gz"
    sha256 "27c43a48497728893a428686e47744242c839c88a767c4e7a54a892f73a14b7e"
  end

  def install
    virtualenv_create(libexec, "python3.12")
    virtualenv_pip_install resources
    system libexec/"bin/pip", "install", *std_pip_args(build_isolation: true), "."
  end

  test do
    assert_match "Q4_K_M", shell_output("#{bin}/mdlcalc 7B")
    assert_match "GB", shell_output("#{bin}/mdlcalc 1T Q8_0")
  end
end
