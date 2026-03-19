class Mdlcalc < Formula
  include Language::Python::Virtualenv

  desc "Calculate approximate memory requirements for LLM inference"
  homepage "https://github.com/SharkyRawr/mdlcalc"
  url "https://github.com/SharkyRawr/mdlcalc/releases/download/v0.1.1/mdlcalc-0.1.1.tar.gz"
  sha256 "7ee630dee06a4e99ab769e9bfb3de90bcb503b099d8379900df8ca32928ab28d"
  license "CC-BY-NC-SA-4.0"

  depends_on "python@3.12"

  bottle do
    root_url "https://github.com/SharkyRawr/mdlcalc/releases/download/v0.1.1"
    rebuild 1
    sha256 cellar: :any_skip_relocation, arm64_sequoia: "3e378e1c3951d851b01051f5b3fbf35c617b5924bdc0a23612cf6df76ed42289"
    sha256 cellar: :any_skip_relocation, arm64_tahoe: "48a4ae1e56526c1f548e7dc3da54ef39d297cdbfd3aeb18b2875d569550b130e"
  end


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
