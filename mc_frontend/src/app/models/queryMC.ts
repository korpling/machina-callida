import {DependencyValue, PartOfSpeechValue, Phenomenon} from 'src/app/models/enum';

export class QueryMC {
    public phenomenon: Phenomenon;
    public values: DependencyValue[] | PartOfSpeechValue[] | string[];
    constructor(init?: Partial<QueryMC>) {
        Object.assign(this, init);
    }
}

