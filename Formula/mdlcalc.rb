class Mdlcalc < Formula
  include Language::Python::Virtualenv

  desc "Calculate approximate memory requirements for LLM inference"
  homepage "https://github.com/SharkyRawr/mdlcalc"
  url "https://github.com/SharkyRawr/mdlcalc/releases/download/v0.1.1/mdlcalc-0.1.0.tar.gz"
  sha256 "9504f58407b8083107d9dbfb7a339549ce1adb30ec3d5e034b3ecd84012d0654"
  license "CC-BY-NC-SA-4.0"

  depends_on "python@3.12"

  resource "click" do
    url "https://files.pythonhosted.org/packages/3d/fa/656b739db8587d7b5dfa22e22ed02566950fbfbcdc20311993483657a5c0/click-8.3.1.tar.gz"
    sha256 "12ff4785d337a1bb490bb7e9c2b1ee5da3112e94a8622f26a6c77f5d2fc6842a"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Q4_K_M", shell_output("#{bin}/mdlcalc 7B")
    assert_match "GB", shell_output("#{bin}/mdlcalc 1T Q8_0")
  end
end
