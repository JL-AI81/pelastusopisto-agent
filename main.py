"""Pääohjelma - testit"""

from agent import PelastusopistoAgent


def main():
    print("=" * 60)
    print("PELASTUSOPISTO-AGENTTI")
    print("=" * 60)
    print()
    
    # Luo agentti
    agent = PelastusopistoAgent()
    print()
    
    # TESTI 1
    print("TESTI 1: Hae pelastusopisto.fi etusivu")
    print("-" * 60)
    vastaus = agent.chat("Hae https://www.pelastusopisto.fi ja kerro mitä sivulla on")
    print()
    print("VASTAUS:")
    print(vastaus)
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()