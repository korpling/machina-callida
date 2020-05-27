import {DependencyValue, PartOfSpeechValue} from 'src/app/models/enum';
import {Phenomenon} from '../../../openapi';

export class QueryMC {
    public phenomenon: Phenomenon;
    public values: DependencyValue[] | PartOfSpeechValue[] | string[];
    constructor(init?: Partial<QueryMC>) {
        Object.assign(this, init);
    }
}

