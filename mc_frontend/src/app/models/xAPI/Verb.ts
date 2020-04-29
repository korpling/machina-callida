import LanguageMap from './LanguageMap';

class Verb {
    id: string;
    display?: LanguageMap;

    constructor(init?: Partial<Verb>) {
        Object.assign(this, init);
    }
}

export default Verb;
