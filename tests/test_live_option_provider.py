from app.data.providers.nse_option_provider import NSEOptionProvider



provider = NSEOptionProvider()



print("=" * 60)
print("LIVE OPTION PROVIDER TEST")
print("=" * 60)



options = provider.get_option_chain(

    "HAL"

)



print()

print(

    "Contracts:",

    len(options)

)



for option in options[:5]:

    print()

    print(option)