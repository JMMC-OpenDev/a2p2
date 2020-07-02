__version__ = "0.2.12"

__release_notes__ = {
    # "0.1.6": {
    #    "STATUS":[
    #             "This version get lot of changes and may contain bugs or missing features, please provide any feedback to improve and prepare a better future release !"
    #         ],
    #    "A2P2": [
    #
    #        ],
    #    "VLTI": [
    #
    #        ],
    #    "CHARA": [
    #
    #        ],
    #    "TODO-SCIENCE": [
    #
    #        ],
    #    "TODO-DEV": [
    #
    #        ],
    #    },
    "0.2.12": {
        "STATUS": [
        ],
        "A2P2": [
            "Fix import in main console script"
        ],
        "VLTI": [
        ],
        "CHARA": [
        ],
        "TODO-SCIENCE": [
        ],
        "TODO-DEV": [
        ],
    },
    "0.2.11": {
        "STATUS": [
        ],
        "A2P2": [
            "enhance setup.py so it install Windows special-cases .exe files"
        ],
        "VLTI": [
        ],
        "CHARA": [
        ],
        "TODO-SCIENCE": [
        ],
        "TODO-DEV": [
        ],
    },
    "0.2.10": {
        "STATUS": [
        ],
        "A2P2": [
            "Patch bad SAMP url handling on Windows"
        ],
        "VLTI": [
        ],
        "CHARA": [
        ],
        "TODO-SCIENCE": [
        ],
        "TODO-DEV": [
        ],
    },
    "0.2.9": {
        "STATUS": [
        ],
        "A2P2": [

        ],
        "VLTI": [
            "Fix bug that prevent to create any folder or concatenation at RUNS's root"
        ],
        "CHARA": [

        ],
        "TODO-SCIENCE": [

        ],
        "TODO-DEV": [

        ],
    },
    "0.2.8": {
        "STATUS": [
        ],
        "A2P2": [
            "Fix release notes order in the GUI",
            "Handle special jmmc account, kindly set by ESO colleagues to perfom future tests as closed as possible to the real UX"
        ],
        "VLTI": [
            "Display instrument package version in the container table",
            "Limit keyword set on P2 only to the modified ones. No more default values from our static config are sent so it enhances compatibility accross multiple Period versions",
        ],
        "CHARA": [
        ],
        "TODO-SCIENCE": [
            "Complete/fix GRAVITY DIT table with P105 changes that will come in the next template user manual",
            "Use a calibrator template for MATISSE (instead of default hyb_obs)",
            "flag ~important~ keywords which MUST be set in a2p2 code and not leaved to there default values"
        ],
        "TODO-DEV": [
            "Support multiple version (two major at least)",
            "Support numlist keyword : eg. SEQ.HWPOFF",
            "Optimize VLTI run chooser : DEMO tests suffer from a long run filtering",
            "unify ob name creation in vlti instrument createOB()"
        ]
    }, "0.2.7": {
        "STATUS": [
            "This version get lot of changes and may contain bugs or missing features, please provide any feedback to improve and prepare a better future release !"
        ],
        "A2P2": [
            "Refactor code accross vlti instruments",
            "Fix container selection in P2 tree"
            "Add release notes in the GUI"
        ],
        "VLTI": [
            "Conf updated with IPs 105.18",
            "Add MATISSE support",
            "Change GRAVITY DIT computation",
            "OB constraints autochecked using an instrumentConstraints TSF",
            "Support Concatenations (also shown in the tree panel)",
            "Show type in the container chooser instead of containerID"
        ],
        "CHARA": [
        ],
        "TODO-SCIENCE": [
            "Complete/fix GRAVITY DIT table with P105 changes that will come in the next template user manual",
            "Use a calibrator template for MATISSE (instead of default hyb_obs)",
            "flag ~important~ keyword that MUST be set in a2p2 code to avoid default"
        ],
        "TODO-DEV": [
            "Support numlist keyword : eg. SEQ.HWPOFF",
            "Optimize VLTI run chooser : DEMO tests suffer from a long run filtering",
            "Do not set default values in a2p2 if not set",
            "unify ob name creation in vlti instrument createOB()"
        ]
    }, "0.2.6": {
        "A2P2": [

        ],
        "VLTI": [
            "Support baseline back again (single one at present)"
        ],
        "CHARA": [

        ]
    },
    "0.2.5": {
        "A2P2": [

        ],
        "VLTI": [
            "Add missing template name in log",
            "Fix error removing baseline after constraint changes on P2 side. Next a2p2 version should add them back in acq templates"
        ],
        "CHARA": [

        ]
    },
    "0.2.4": {
        "A2P2": [

        ],
        "VLTI": [
            "Fix bug / wrong keys"
        ],
        "CHARA": [

        ]
    },
    "0.2.3": {
        "A2P2": [

        ],
        "VLTI": [
            "Hide password in login frame"
        ],
        "CHARA": [

        ]
    },
    "0.2.2": {
        "A2P2": [

        ],
        "VLTI": [
            "ignore default time constraints computed by Aspro"
        ],
        "CHARA": [

        ]
    },
    "0.2.1": {
        "A2P2": [

        ],
        "VLTI": [
            "fix support for a list of multiples time constraints"
        ],
        "CHARA": [

        ]
    },
    "0.2.0": {
        "A2P2": [

        ],
        "VLTI": [
            "bug fix"
        ],
        "CHARA": [

        ]
    },
    "0.1.6": {
        "A2P2": [
            "Major code reformating - pep8 compliant"
        ],
        "VLTI": [
            "general config updates",
            "add PIONIER"
        ],
        "CHARA": [

        ]
    },
    "0.1.5": {
        "A2P2": [

        ],
        "VLTI": [
            "bugfix for dualfield cases"
        ],
        "CHARA": [

        ]
    },
    "0.1.4": {
        "A2P2": [
            "fix order of returned fluxes in OB.getFluxes()"
        ]
    },
    "0.1.3": {
        "VLTI": [
            "fix telescope mode computation"
        ]
    },
    "0.1.2": {
        "A2P2": [
            "bugfix for SPLIT polarisation mode detection on GRAVITY",
            "bugfix that displays warning message during DIT calculation in GRAVITY LR mode",
            "enhancement of out of bound exception message of DIT calculation method"
        ]
    },
    "0.1.1": {
        "A2P2": [
            "muti-faciliy",
            "multi-VltiInstruments",
            "json VltiConfig (templates+dit tables)"
        ]
    }
}
