try:
    from ..agent.c88xx_agent_base import C88xxAgentBase
except:
    # for current dir test
    import sys
    sys.path.append("../")
    from  agent.c88xx_agent_base import C88xxAgentBase

class C88xxAnalyzerBase(object):
    # ------------------------------------------------------
    # class attribute & method
    # ------------------------------------------------------
    _analyzer_classes = {}
    _config_agent = None
    _analyzers = {}

    @classmethod
    def register(cls, analyzer_type):
        '''
        analyzer_type:

        '''
        def inner(analyzer_class):
            if not issubclass(analyzer_class, cls):
                print("Error %s is not instance of %s" % (analyzer_class, cls))
                return analyzer_class

            key = str(analyzer_type).lower()
            if key in cls._analyzer_classes:
                # XXX ??? call with logger
                print("Warning %s is already registered in the ResourceManager. "
                      "Overwriting with %s" % (key, analyzer_class))
            cls._analyzer_classes[key] = analyzer_class
            return analyzer_class
        return inner

    @classmethod
    def get_analyzer(cls, analyzer_type):
        '''
        info:   UIR or analyzer_type
        Singleton, agent will auto config when changing agent
        '''
        key = str(analyzer_type).lower()
        analyzer = cls._analyzers.get(key, None)
        if analyzer:
            return analyzer

        analyzer_cls = cls._analyzer_classes.get(key, None)
        if not analyzer_cls:
            return None

        analyzer = analyzer_cls()
        if cls._config_agent:
            analyzer.set_agent(cls._config_agent)
        cls._analyzers[key] = analyzer
        return analyzer

    @classmethod
    def list_analyzer(cls):
        return cls._analyzer_classes.keys()

    @classmethod
    def config_agent(cls, agent):
        '''
        auto config all the analyzer which is the result by get_analyzer()
        '''
        if not agent: cls._config_agent = None

        assert(isinstance(agent, C88xxAgentBase))
        for name, analyzer in cls._analyzers.items():
            analyzer.set_agent(agent)

    @classmethod
    def gen_offline_analyzer(cls, analyzer_type):
        '''
        Just return an analyzer by type;
        Do not configurate agent for the analyzer.
        '''
        key = str(analyzer_type).lower()
        analyzer_cls = cls._analyzer_classes.get(key, None)
        if not analyzer_cls:
            return None
        return analyzer_cls()

    # ------------------------------------------------------
    # interface
    # ------------------------------------------------------
    def __init__(self, agent = None):
        if agent:
            assert(isinstance(agent, C88xxAgentBase))
        self.agent = agent

    def set_agent(self, agent):
        assert(isinstance(agent, C88xxAgentBase))
        self.agent = agent
