import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, inject, TestBed} from '@angular/core/testing';

import {AuthorDetailPage} from './author-detail.page';
import {RouterModule} from '@angular/router';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {APP_BASE_HREF} from '@angular/common';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import Spy = jasmine.Spy;
import {CorpusMC} from '../models/corpusMC';

describe('AuthorDetailPage', () => {
    let authorDetailPage: AuthorDetailPage;
    let fixture: ComponentFixture<AuthorDetailPage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [AuthorDetailPage],
            imports: [
                HttpClientTestingModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        })
            .compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(AuthorDetailPage);
        authorDetailPage = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(authorDetailPage).toBeTruthy();
    });

    it('should show possible references', () => {
        const currentCorpusSpy: Spy = spyOn(authorDetailPage.corpusService, 'setCurrentCorpus');
        const textRangeSpy: Spy = spyOn(authorDetailPage.helperService, 'goToTextRangePage').and.returnValue(Promise.resolve(true));
        authorDetailPage.showPossibleReferences(new CorpusMC());
        expect(currentCorpusSpy).toHaveBeenCalledTimes(1);
        expect(textRangeSpy).toHaveBeenCalledTimes(1);
    });
});
