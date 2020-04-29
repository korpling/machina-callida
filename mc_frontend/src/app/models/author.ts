import {CorpusMC} from 'src/app/models/corpusMC';

export class Author {
    public corpora: CorpusMC[];
    public name: string;
    constructor(init?: Partial<Author>) {
        Object.assign(this, init);
    }
}

