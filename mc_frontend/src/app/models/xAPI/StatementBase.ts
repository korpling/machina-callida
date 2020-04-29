import Actor from './Actor';
import Attachment from './Attachment';
import Verb from './Verb';
import Context from './Context';
import Result from './Result';
import StatementObject from './StatementObject';

class StatementBase {
    actor: Actor;
    object: StatementObject;
    verb: Verb;
    context?: Context;
    result?: Result;
    attachments?: Attachment[];

    constructor(init?: Partial<StatementBase>) {
        Object.assign(this, init);
    }
}

export default StatementBase;
