/* tslint:disable:variable-name */
import {Citation} from 'src/app/models/citation';

export class CorpusMC {
    public author: string;
    public cid: number;
    public source_urn: string;
    public title: string;
    public citation_level_1: string;
    public citation_level_2: string;
    public citation_level_3: string;
    public citations: { [label: string]: Citation; };
    constructor(init?: Partial<CorpusMC>) {
        Object.assign(this, init);
    }
}
