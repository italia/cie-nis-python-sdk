from pkg.lib.CIEInterface import CIEInterface


def main():
    interface = CIEInterface()
    interface.mrtdAuth('YYMMDD', 'YYMMDD', '*********')
    data = interface.extractData()

    print(data)

if __name__ == "__main__":
    main()
