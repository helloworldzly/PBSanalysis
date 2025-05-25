

# Decentralized Exchanges
SWAP_UNISWAP_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822" # UNISWAP V2/Sushiswap (Swap)  # yes
SWAP_UNISWAP_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67" # UNISWAP V3 (Swap)  # yes
BALANCER        = "0x908fb5ee8f16c6bc9bc3690973819f32a4d4b10188134543c88706e0e1d43378" # BALANCER (LOG_SWAP) #yes
CURVE_1         = "0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b" # CURVE (TokenExchangeUnderlying) #yes
CURVE_2         = "0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140" # CURVE (TokenExchange) # yes
BANCOR          = "0x276856b36cbc45526a0ba64f44611557a2a8b68662c5388e9fe6d72e86e1c8cb" # BANCOR (Conversion)  # yes
ZERO_EX_1       = "0x6869791f0a34781b29882982cc39e882768cf2c96995c2a110c577c53bc932d5" # 0x Protocol (Fill)
ZERO_EX_2       = "0xab614d2b738543c0ea21f56347cf696a3a0c42a7cbec3212a5ca22a4dcff2124" # 0x Protocol   #yes
ZERO_EX_3       = "0x829fa99d94dc4636925b38632e625736a614c154d55006b7ab6bea979c210c32" # 0x Protocol

# Flash loans
AAVE_FLASH_LOAN = "0x5b8f46461c1dd69fb968f1a003acee221ea3e19540e350233b612ddb43433b55" # Aave Flash Loan (FlashLoan)
#DYDX_WITHDRAW   = "0xbc83c08f0b269b1726990c8348ffdf1ae1696244a14868d766e542a2f18cd7d4" # dYdX Flash Loan (LogWithdraw)
#DYDX_DEPOSIT    = "0x2bad8bc95088af2c247b30fa2b2e6a0886f88625e0945cd3051008e0e270198f" # dYdX Flash Loan (LogDeposit)


# Liquidation platforms
AAVE_V1         = "0x56864757fd5b1fc9f38f5f3a981cd8ae512ce41b902cf73fc506ee369c6bc237" # Aave Protocol V1 (LiquidationCall)
AAVE_V2         = "0xe413a321e8681d831f4dbccbca790d2952b56f977908e45be37335533e005286" # Aave Protocol V2 (LiquidationCall) #yes
#COMPOUND_V1     = "0x196893d3172b176a2d1d257008db8d8d97c8d19c485b21a653c309df6503262f" # Compound V1 (LiquidateBorrow)
COMPOUND_V2     = "0x298637f684da70674f26509b10f07ec2fbc77a335ab1e7d6215a4b2484d8bb52" # Compound V2 (LiquidateBorrow)
#DYDX_LIQUIDATE  = "0x1b9e65b359b871d74b1af1fc8b13b11635bfb097c4631b091eb762fda7e67dc7" # dYdX (LogLiquidate)
#OPYN            = "0xcab8e1abb9f8235c6db895cf185336dc9461aecf477b98c1be83687ee549e66a" # opyn (Liquidate)


# OTHERS

TRANSFER       = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" # ERC20 "Transfer"
TOKEN_PURCHASE = "0xcd60aa75dea3072fbc07ae6d7d856b5dc5f4eee88854f5b4abf7b680ef8bc50f" # Uniswap V1 "TokenPurchase"
ETH_PURCHASE   = "0x7f4091b46c33e918a0f3aa42307641d17bb67029427a5369e54b353984238705" # Uniswap V1 "ETHPurchase"


TOKEN_AMOUNT_DELTA = 0.01 # Maximum different between buying and selling amount of tokens. Default value is 1%.



# Wrapper Ether
coin_address_dict = {}
coin_address_dict["0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"] = "WETH"
