
from .power_of import PowerOfGenerator
from .cert import CertGenerator
import sys


if sys.argv[1] == "power_of":
    generator = PowerOfGenerator(sys.argv[2], sys.argv[3], sys.argv[4])
    generator.add_names(sys.argv[5], sys.argv[6])

elif sys.argv[1] == "cert":
    generator = CertGenerator(sys.argv[2], sys.argv[3], sys.argv[4])
    generator.add_names(
        sys.argv[5],
        sys.argv[6],
        "0x11c667ef288cab58f606786f6a0e89a3789d6416",
        "0x11c667ef288cab58f606786f6a0e89a3789d6416"
    )
    generator.add_contract_id("0x11c667ef288cab58f606786f6a0e89a3789d6416")
    generator.add_expiration_date(10)
    generator.save()
