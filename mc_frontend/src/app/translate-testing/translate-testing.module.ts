import {EventEmitter, Injectable, NgModule, Pipe, PipeTransform} from '@angular/core';
import {TranslateLoader, TranslateModule, TranslatePipe, TranslateService} from '@ngx-translate/core';
import {Observable, of} from 'rxjs';
import {
    DefaultLangChangeEvent,
    LangChangeEvent,
    TranslationChangeEvent
} from '@ngx-translate/core/lib/translate.service';


const translations: any = {};

export class FakeLoader implements TranslateLoader {
    getTranslation(lang: string): Observable<any> {
        return of(translations);
    }
}

@Pipe({
    name: 'translate'
})
export class TranslatePipeMock implements PipeTransform {
    public name = 'translate';

    public transform(query: string, ...args: any[]): any {
        return query;
    }
}

@Injectable()
export class TranslateServiceStub {
    currentLang = 'en';
    onDefaultLangChange: EventEmitter<DefaultLangChangeEvent> = new EventEmitter<DefaultLangChangeEvent>();
    readonly onLangChange: EventEmitter<LangChangeEvent> = new EventEmitter<LangChangeEvent>();
    onTranslationChange: EventEmitter<TranslationChangeEvent> = new EventEmitter<TranslationChangeEvent>();

    public get<T>(key: T): Observable<T> {
        return of(key);
    }

    public setDefaultLang(lang: string) {
    }

    public getDefaultLang() {
        return 'en';
    }

    public getBrowserLang(): string {
        return 'en';
    }

    public use(lang: string): Observable<any> {
        this.currentLang = lang;
        return of(true);
    }
}

@NgModule({
    declarations: [
        TranslatePipeMock
    ],
    providers: [
        {
            provide: TranslateService,
            useClass: TranslateServiceStub
        },
        {
            provide: TranslatePipe,
            useClass: TranslatePipeMock
        },
    ],
    imports: [
        TranslateModule.forRoot({
            loader: {
                provide: TranslateLoader,
                useClass: FakeLoader
            },
        })
    ],
    exports: [
        TranslatePipeMock,
        TranslateModule
    ]
})
export class TranslateTestingModule {
}
