class C88xxAgentBase(object):
    # ------------------------------------------------------
    # class attribute & method
    # ------------------------------------------------------
    _agent_classes = {}

    @classmethod
    def register(cls, agent_type):
        '''
        agent_type: URI protocol; such as "mmp", "scip"

        '''
        def inner(agent_class):
            if not issubclass(agent_class, cls):
                print("Error %s is not instance of %s" % (agent_class, cls))
                return agent_class

            key = str(agent_type).lower()
            if key in cls._agent_classes:
                # XXX ??? call with logger
                print("Warning %s is already registered in the ResourceManager. "
                      "Overwriting with %s" % (key, agent_class))
            cls._agent_classes[key] = agent_class
            return agent_class
        return inner

    @classmethod
    def get_agent(cls, info):
        '''
        info:   UIR or agent_type
        '''
        infos = info.split("://")
        key = str(infos[0]).lower()
        agent_cls = cls._agent_classes.get(key, None)
        if not agent_cls:
            return None

        try:
            agent = agent_cls()
            if len(infos) > 1:
                # setting with URI
                agent.open(info)
            return agent
        except:
            return None

    @classmethod
    def list_agent(cls):
        return cls._agent_classes.keys()

    # ------------------------------------------------------
    # interface
    # ------------------------------------------------------
    # return nothing
    def open(self, uri):
        '''
        open an agent

        input:
        uri:
            eg: "mmp://eth0"
            eg: "scpi://192.168.36.2"
            eg: "usb://???"
        output:
            Nothing
        '''
        raise NotImplementedError

    def close(self):
        '''
        output:
            Nothing
        '''
        raise NotImplementedError

    def get_oam(self, llid, reg):
        '''
        input:
        llid: uint8, 0x7e means self
                     0x7f means remote all
                     else llid
        reg:  uint8
        -------
        output:
        Success: uint16
        Fail:    None
        '''
        # TODO: check llid & reg
        raise NotImplementedError

    def set_oam(self, llid, reg, data):
        '''
        input:
        llid: uint8, 0x7e means self
                     0x7f means remote all
                     else llid
        reg:  uint8
        data: uint16
        -------
        output:
        Success: not None
        Fail:    None
        '''
        # TODO: check llid & reg
        raise NotImplementedError

    def get_ana(self, reg):
        '''
        input:
        reg:  uint8
        -------
        output:
        Success: uint16
        Fail:    None
        '''
        raise NotImplementedError

    def set_ana(self, reg, data):
        '''
        input:
        reg:  uint8
        data: uint16
        -------
        output:
        Success: not None
        Fail:    None
        '''
        raise NotImplementedError

    def get_tuner(self, reg):
        '''
        input:
        reg: uint8
        -------
        output:
        Success: uint8
        Fail: None
        '''
        raise NotImplementedError

    def set_tuner(self, reg, data):
        '''
        input:
        reg: uint8
        data: uint8
        -------
        output:
        Success: not None
        Fail: None
        '''
        raise NotImplementedError

    def setup_dbgc(self, cs, tr_event, tp, tr_mode):
        '''
        input:
        cs:         uint16, trigger clock selection
        tr_event    uint16, trigger event selection
        tp          uint16, capture point selection, capture number selection
        tr_mode     uint16, capture mode selection, pre_capture_point selection
        -------
        output:
        Success: not None
        Fail:    None
        '''
        raise NotImplementedError

    def dump_dbgc(self, samples):
        '''
        input:
        sample: samples times(usaully 2048/8192)
        -------
        output:
        Success: [uint16, ...]
        Fail:    None
        '''
        raise NotImplementedError

    def list_resource(self):
        '''
        return {resource:desc}
        '''
        raise NotImplementedError

    def uri_help(self, samples):
        '''
        return uri help info
        '''
        pass

    class AgentOpenException(Exception):
        pass
