import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {IonicModule} from '@ionic/angular';
import {CommonModule} from '@angular/common';
import {AuthorPage} from 'src/app/author/author.page';
import {TranslateModule} from '@ngx-translate/core';
import {FormsModule} from '@angular/forms';

const routes: Routes = [
    {
        path: '',
        component: AuthorPage
    }
];

@NgModule({
    declarations: [
        AuthorPage,
    ],
    imports: [
        CommonModule,
        FormsModule,
        IonicModule,
        RouterModule.forChild(routes),
        TranslateModule.forChild()
    ],
})
export class AuthorPageModule {
}
