import ContextActivities from './ContextActivities';
import Extensions from './Extensions';
import Group from './Group';
import Agent from './Agent';

class Context {
    contextActivities?: ContextActivities;
    team?: Group;
    instructor?: Agent;
    registration?: string;
    extensions?: Extensions;

    constructor(init?: Partial<Context>) {
        Object.assign(this, init);
    }
}

export default Context;
